import json
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backend_bases import MouseEvent
from matplotlib.ticker import FuncFormatter
from ortools.sat.python import cp_model
from statsmodels.nonparametric.smoothers_lowess import lowess

# ---------- Matplotlib 中文与外观 ----------
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


# 绘制曲线
def plot_power_curves(items, title='功率测量与预测', figsize=(60, 20)):
    times = [datetime.strptime(i["timePoint"], "%Y-%m-%d %H:%M:%S") for i in items]
    measured = [float(i["measuredPower"]) for i in items]
    predicted = [float(i["predictPower"]) for i in items]

    fig, ax = plt.subplots(figsize=figsize, dpi=100)
    plt.rcParams.update({'font.size': 26, 'lines.linewidth': 3})
    ax.plot(times, measured, label='实际出力', marker='o', color='orange', markersize=8)
    ax.plot(times, predicted, label='预测功率', marker='o', color='grey', markersize=8, alpha=0.5)

    # 绘制调节预测功率曲线 （如果存在）
    if "adjustedPowerFirst" in items[0]:
        first_adjusted = [float(idx["adjustedPowerFirst"]) for idx in items]
        ax.plot(times, first_adjusted, label='初次调节预测功率', marker='o', color='green', markersize=8, alpha=0.5)
        # 绘制调节预测功率曲线 （如果存在）
    if "adjustedPower" in items[0]:
        adjusted = [float(idx["adjustedPower"]) for idx in items]
        ax.plot(times, adjusted, label='最终调节预测功率', marker='o', color='blue', markersize=8, alpha=0.5)

    ax.set_title(title, fontsize=30, pad=20)
    ax.set_xlabel('时间', fontsize=26)
    ax.set_ylabel('功率 (MW)', fontsize=26)
    ax.legend(fontsize=26)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.2f}'))
    fig.autofmt_xdate()

    def on_move(event: MouseEvent, mdates=None):
        if event.inaxes == ax and event.xdata and event.ydata:
            x_dt = mdates.num2date(event.xdata)
            ax.set_title(f"{title}\n时间: {x_dt:%Y-%m-%d %H:%M:%S} | 功率: {event.ydata:.2f}",
                         fontsize=30, pad=20)
            fig.canvas.draw_idle()

    fig.canvas.mpl_connect('motion_notify_event', on_move)
    plt.tight_layout()
    plt.show(block=True)


# 计算弃电量
def get_discharge(items, start_time, end_time):
    s_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    e_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    total = 0.0
    for e in items:
        tp = datetime.strptime(e["timePoint"], "%Y-%m-%d %H:%M:%S")
        if s_dt <= tp <= e_dt:
            m, p = float(e["measuredPower"]), float(e.get("adjustedPower", e["predictPower"]))
            total += max(p - m, 0) * 5 / 60 / 10
    return total


# 平滑曲线
def apply_lowess_smoothing(predictions, frac=0.2, it=3):
    """应用LOWESS平滑算法到预测功率数据"""
    x = np.arange(len(predictions))
    smoothed = lowess(predictions, x, frac=frac, it=it, return_sorted=False)
    return smoothed


# 智能调节
def smart_adjust(power_list, period_start, period_end, target_discharge, capacity_upper, max_step=4.0, lowess_frac=0.1,
                 lowess_it=1):
    """
    items数据结构：[
       {
         "timePoint": "2025-04-16 00:00:00", # 每五分钟一个时间点
         "measuredPower": "0.0000",  #功率值（兆瓦）
         "predictPower": "0.0000" #功率值（兆瓦）
       }
       ....
     ]
     1、通过变动源数据中predictPower每个点的值，在 startTime和endTime范围内调整使其弃电量的值等于target_discharge
     2、调整完成的曲线保持平滑但要大致保持原有趋势，不要骤降骤升和一条平线
     3、可以适当调整period_start和period_end范围外的predict_power曲线。以配合范围内曲线趋势的变化
     4、给出最终调整完成的每个时间点的调整值（兆瓦）
    """
    period_start, period_end = [datetime.strptime(t, "%Y-%m-%d %H:%M:%S") for t in (period_start, period_end)]
    # 0、保存原始预测功率
    for power in power_list:
        power["adjustedPower"] = power.get("adjustedPower", power["predictPower"])
    # 1. 收集窗口内点
    idx_info = [(idx, float(it["measuredPower"]), float(it["adjustedPower"]))
                for idx, it in enumerate(power_list)
                if period_start <= datetime.strptime(it["timePoint"], "%Y-%m-%d %H:%M:%S") <= period_end]
    if not idx_info:
        raise ValueError("时间窗口与数据不匹配。")

    n = len(idx_info)
    capacity_kw = int(round(capacity_upper * 1000))
    step_kw = int(round(max_step * 1000))
    target_power_gap = int(round(target_discharge * 120 * 1000))

    # 2. 先对原始预测功率应用LOWESS平滑
    adjusted_power = [orig for _, _, orig in idx_info]
    smoothed = apply_lowess_smoothing(adjusted_power, frac=lowess_frac, it=lowess_it)

    # 3. 重新缩放以满足弃电量目标
    measured = [meas for _, meas, _ in idx_info]
    surplus_smoothed = np.maximum(smoothed - measured, 0)
    current_energy = np.sum(surplus_smoothed) * 5 / 60 / 10  # 转换为万kWh

    if current_energy > 0:
        scale_factor = target_discharge / current_energy
        scaled_adjusted = measured + (smoothed - measured) * scale_factor
    else:
        scaled_adjusted = smoothed

    # 4、确保不超过容量限制
    scaled_adjusted = np.clip(scaled_adjusted, 0, capacity_upper)

    # 5、现在以平滑缩放后的曲线为基础进行约束求解
    m = cp_model.CpModel()
    pred = [m.NewIntVar(0, capacity_kw, f"pred_{i}") for i in range(n)]
    surplus = [m.NewIntVar(0, capacity_kw, f"sur_{i}") for i in range(n)]

    # 5.1、 surplus_i = max(pred_i - measured_i, 0)
    for idx, (_, meas, _) in enumerate(idx_info):
        measured_kw = int(round(meas * 1000))
        diff = m.NewIntVar(-capacity_kw, capacity_kw, f"diff_{idx}")
        m.Add(diff == pred[idx] - measured_kw)
        m.AddMaxEquality(surplus[idx], [diff, 0])

    # 5.2、 平滑约束 (窗口内部)
    for idx in range(1, n):
        m.Add(pred[idx] - pred[idx - 1] <= step_kw)
        m.Add(pred[idx - 1] - pred[idx] <= step_kw)

    # 5.3、 平滑约束
    first_idx, last_idx = idx_info[0][0], idx_info[-1][0]

    if first_idx > 0:  # 左边还有点
        pre_point = float(power_list[first_idx - 1]["adjustedPower"])
        pre_point_kw = int(round(pre_point * 1000))
        m.Add(pred[0] - pre_point_kw <= step_kw)
        m.Add(pre_point_kw - pred[0] <= step_kw)

    if last_idx < len(power_list) - 1:  # 右边还有点
        next_point = float(power_list[last_idx + 1]["adjustedPower"])
        next_point_kw = int(round(next_point * 1000))
        m.Add(pred[-1] - next_point_kw <= step_kw)
        m.Add(next_point_kw - pred[-1] <= step_kw)

    # 5.4. 弃电量等式
    m.Add(sum(surplus) == target_power_gap)

    # 6. 目标：最小化与平滑缩放后曲线的差异
    abs_delta = []
    for idx, scaled_val in enumerate(scaled_adjusted):
        scaled_kW = int(round(scaled_val * 1000))
        d = m.NewIntVar(-capacity_kw, capacity_kw, f"d_{idx}")
        m.Add(d == pred[idx] - scaled_kW)
        u = m.NewIntVar(0, capacity_kw, f"u_{idx}")
        v = m.NewIntVar(0, capacity_kw, f"v_{idx}")
        m.Add(d == u - v)
        m.Add(d >= -u)
        m.Add(d <= v)
        abs_delta.append(u + v)

    m.Minimize(sum(abs_delta))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 5
    solver.parameters.num_search_workers = 16
    if solver.Solve(m) not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError("求解失败：无可行解。")

    # 7、 获取调整结果
    final_adjusted = [solver.Value(pred[idx]) / 1000.0 for idx in range(n)]

    # 8、 写回结果
    idx2newpred = {idx: final_adjusted[i] for i, (idx, _, _) in enumerate(idx_info)}
    new_items = []
    for idx, it in enumerate(power_list):
        it = it.copy()
        if idx in idx2newpred:
            new_p = idx2newpred[idx]
            it["delta"] = f"{new_p - float(it['adjustedPower']):+.3f}"
            it["adjustedPower"] = f"{new_p:.3f}"
        else:
            it["delta"] = "+0.000"
        new_items.append(it)

    # 9、 精度检查
    actual = get_discharge(new_items, period_start.strftime("%Y-%m-%d %H:%M:%S"),
                           period_end.strftime("%Y-%m-%d %H:%M:%S"))
    if abs(actual - target_discharge) > 1e-6:
        print(f"调整误差 {actual - target_discharge:.6f} 万kWh")
    return new_items


# ---------- 直接运行 ----------
if __name__ == "__main__":
    capacity = 50.0
    targetDischarge = 5.5820  # 万kWh
    startTime = "2025-04-16 07:00:00"
    endTime = "2025-04-16 17:00:00"

    with open("data.json", encoding="utf-8") as f:
        data = json.load(f)

    print("调整前弃电量:", f"{get_discharge(data, startTime, endTime):.4f} 万kWh")
    for i in range(0, 20):
        # 初次调整
        adjusted = smart_adjust(data, startTime, endTime, targetDischarge + i * 2, capacity, max_step=2.0,
                                lowess_frac=0.3, lowess_it=2)
        for item in adjusted:
            item["adjustedPowerFirst"] = item["adjustedPower"]
        # 回归调整
        adjusted = smart_adjust(adjusted, startTime, endTime, targetDischarge + i * 2, capacity, max_step=2.0)
        print("调整后弃电量:", f"{get_discharge(adjusted, startTime, endTime):.4f} 万kWh")
        # 绘制曲线
        plot_power_curves(adjusted)
