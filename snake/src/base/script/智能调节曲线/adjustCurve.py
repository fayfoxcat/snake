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


def plot_power_curves(items, adjusted_items=None, title='功率测量与预测', figsize=(60, 20)):
    times = [datetime.strptime(i["timePoint"], "%Y-%m-%d %H:%M:%S") for i in items]
    measured = [float(i["measuredPower"]) for i in items]
    predicted = [float(i["predictPower"]) for i in items]

    # 获取原始预测功率（如果存在）
    original_predicted = None
    if "originalPredictPower" in items[0]:
        original_predicted = [float(i["originalPredictPower"]) for i in items]

    # 如果有调整后的数据，获取调整后的预测值
    adjusted_predicted = None
    if adjusted_items is not None:
        adjusted_predicted = [float(i["predictPower"]) for i in adjusted_items]

    fig, ax = plt.subplots(figsize=figsize, dpi=100)
    plt.rcParams.update({'font.size': 26, 'lines.linewidth': 3})
    ax.plot(times, measured, label='实际出力', marker='o', color='green', markersize=8)
    ax.plot(times, predicted, label='当前预测功率', marker='o', color='red', markersize=8, alpha=0.5)

    # 绘制原始预测功率曲线
    if original_predicted is not None:
        ax.plot(times, original_predicted, label='原始预测功率', marker='o', color='orange', markersize=8, alpha=0.5)

    # 如果有调整后的数据，绘制调整后的曲线
    if adjusted_predicted is not None:
        ax.plot(times, adjusted_predicted, label='调整后可用功率', marker='o', color='blue', markersize=8)

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


# ---------- 计算弃电量 ----------
def get_discharge(items, start_time, end_time):
    s_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    e_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    total = 0.0
    for e in items:
        tp = datetime.strptime(e["timePoint"], "%Y-%m-%d %H:%M:%S")
        if s_dt <= tp <= e_dt:
            m, p = float(e["measuredPower"]), float(e["predictPower"])
            total += max(p - m, 0) * 5 / 60 / 10
    return total


def apply_lowess_smoothing(predictions, frac=0.2, it=3):
    """应用LOWESS平滑算法到预测功率数据"""
    x = np.arange(len(predictions))
    smoothed = lowess(predictions, x, frac=frac, it=it, return_sorted=False)
    return smoothed


# ---------- 智能调节 ----------
def smart_adjust(items, start_dt, end_dt, target_discharge, capacity, max_step=2.0, lowess_frac=0.5, lowess_it=3):
    """窗口内调 predictPower，使弃电量精准匹配且曲线平滑。"""
    start_dt, end_dt = [datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                        for t in (start_dt, end_dt)]
    # 保存原始预测功率
    for item in items:
        item["originalPredictPower"] = item["predictPower"]
    # 1. 收集窗口内点
    idx_info = [(idx,
                 float(it["measuredPower"]),
                 float(it["predictPower"]))
                for idx, it in enumerate(items)
                if start_dt <= datetime.strptime(it["timePoint"], "%Y-%m-%d %H:%M:%S") <= end_dt]
    if not idx_info:
        raise ValueError("时间窗口与数据不匹配。")

    n = len(idx_info)
    cap_kW = int(round(capacity * 1000))
    step_kW = int(round(max_step * 1000))
    energy_target_kW5min = int(round(target_discharge * 120 * 1000))

    m = cp_model.CpModel()
    pred = [m.NewIntVar(0, cap_kW, f"pred_{i}") for i in range(n)]
    surplus = [m.NewIntVar(0, cap_kW, f"sur_{i}") for i in range(n)]

    # 2. surplus_i = max(pred_i - measured_i, 0)
    for i, (_, meas, _) in enumerate(idx_info):
        meas_kW = int(round(meas * 1000))
        diff = m.NewIntVar(-cap_kW, cap_kW, f"diff_{i}")
        m.Add(diff == pred[i] - meas_kW)
        m.AddMaxEquality(surplus[i], [diff, 0])

    # 3. 平滑约束 (窗口内部)
    for i in range(1, n):
        m.Add(pred[i] - pred[i - 1] <= step_kW)
        m.Add(pred[i - 1] - pred[i] <= step_kW)

    # 3.1 平滑约束 (窗口边界&hArr;原曲线)
    first_idx, last_idx = idx_info[0][0], idx_info[-1][0]

    if first_idx > 0:  # 左边还有点
        orig_prev = float(items[first_idx - 1]["predictPower"])
        orig_prev_kW = int(round(orig_prev * 1000))
        m.Add(pred[0] - orig_prev_kW <= step_kW)
        m.Add(orig_prev_kW - pred[0] <= step_kW)

    if last_idx < len(items) - 1:  # 右边还有点
        orig_next = float(items[last_idx + 1]["predictPower"])
        orig_next_kW = int(round(orig_next * 1000))
        m.Add(pred[-1] - orig_next_kW <= step_kW)
        m.Add(orig_next_kW - pred[-1] <= step_kW)

    # 4. 弃电量等式
    m.Add(sum(surplus) == energy_target_kW5min)

    # 5. 目标：最小化调整量
    abs_delta = []
    for i, (_, _, orig) in enumerate(idx_info):
        orig_kW = int(round(orig * 1000))
        d = m.NewIntVar(-cap_kW, cap_kW, f"d_{i}")
        m.Add(d == pred[i] - orig_kW)
        u = m.NewIntVar(0, cap_kW, f"u_{i}")
        v = m.NewIntVar(0, cap_kW, f"v_{i}")
        m.Add(d == u - v)
        m.Add(d >= -u)
        m.Add(d <= v)
        abs_delta.append(u + v)

    m.Minimize(sum(abs_delta))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30
    solver.parameters.num_search_workers = 16
    if solver.Solve(m) not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError("求解失败：无可行解。")

    # 6. 获取初步调整结果
    initial_adjusted = [solver.Value(pred[i]) / 1000.0 for i in range(n)]

    # 7. 应用LOWESS平滑
    smoothed = apply_lowess_smoothing(initial_adjusted, frac=lowess_frac, it=lowess_it)

    # 8. 重新缩放以满足弃电量目标
    measured = [meas for _, meas, _ in idx_info]
    surplus_smoothed = np.maximum(smoothed - measured, 0)
    current_energy = np.sum(surplus_smoothed) * 5 / 60 / 10  # 转换为万kWh

    if current_energy > 0:
        scale_factor = target_discharge / current_energy
        final_adjusted = measured + (smoothed - measured) * scale_factor
    else:
        final_adjusted = smoothed

    # 确保不超过容量限制
    final_adjusted = np.clip(final_adjusted, 0, capacity)

    # 9. 写回结果
    idx2newpred = {idx: final_adjusted[i]
                   for i, (idx, _, _) in enumerate(idx_info)}
    new_items = []
    for i, it in enumerate(items):
        it = it.copy()
        if i in idx2newpred:
            new_p = idx2newpred[i]
            it["delta"] = f"{new_p - float(it['predictPower']):+.3f}"
            it["predictPower"] = f"{new_p:.3f}"
        else:
            it["delta"] = "+0.000"
        new_items.append(it)

    # 10. 精度检查
    actual = get_discharge(new_items, start_dt.strftime("%Y-%m-%d %H:%M:%S"),
                           end_dt.strftime("%Y-%m-%d %H:%M:%S"))
    # if abs(actual - target_discharge) > energy_tol:
    #     raise RuntimeError(
    #         f"弃电量 {actual:.6f} 万kWh &ne; 目标 {target_discharge:.6f}")

    return new_items


# ---------- 直接运行 ----------
if __name__ == "__main__":
    capacity = 50.0
    targetDischarge = 30  # 万kWh
    startTime = "2025-04-16 06:00:00"
    endTime = "2025-04-16 17:00:00"

    with open("data.json", encoding="utf-8") as f:
        data = json.load(f)

    print("调整前弃电量:",
          f"{get_discharge(data, startTime, endTime):.4f} 万kWh")
    for i in range(0, 20):
        adjusted = smart_adjust(
            data, startTime, endTime, targetDischarge, capacity,
            max_step=2.0, lowess_frac=0.2, lowess_it=3
        )

        print("调整后弃电量:",
              f"{get_discharge(adjusted, startTime, endTime):.4f} 万kWh")

        # 如果需要可视化
        plot_power_curves(adjusted)
