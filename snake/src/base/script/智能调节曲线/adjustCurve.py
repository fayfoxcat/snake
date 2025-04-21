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
                 lowess_it=1, extend_by=12):
    # Convert period times to datetime
    period_start = datetime.strptime(period_start, "%Y-%m-%d %H:%M:%S")
    period_end = datetime.strptime(period_end, "%Y-%m-%d %H:%M:%S")

    # Preserve original adjustedPower
    for item in power_list:
        item["adjustedPower"] = item.get("adjustedPower", item["predictPower"])

    # 1. Identify original window indices and extend the range
    window_indices = []
    for idx, item in enumerate(power_list):
        tp = datetime.strptime(item["timePoint"], "%Y-%m-%d %H:%M:%S")
        if period_start <= tp <= period_end:
            window_indices.append(idx)
    if not window_indices:
        raise ValueError("时间窗口与数据不匹配。")
    min_idx, max_idx = min(window_indices), max(window_indices)

    # Extend the adjustment window
    extended_min = max(0, min_idx - extend_by)
    extended_max = min(len(power_list)-1, max_idx + extend_by)
    extended_indices = list(range(extended_min, extended_max + 1))
    original_window = set(window_indices)

    # Collect extended window data
    idx_info = [
        (idx, float(power_list[idx]["measuredPower"]), float(power_list[idx]["adjustedPower"]))
        for idx in extended_indices
    ]

    # 2. Apply LOWESS smoothing to the extended window
    adjusted_power = [orig for _, _, orig in idx_info]
    smoothed = apply_lowess_smoothing(adjusted_power, frac=lowess_frac, it=lowess_it)

    # 3. Scale only the original window points
    measured_in_orig = []
    smoothed_in_orig = []
    for i, (idx, meas, _) in enumerate(idx_info):
        if idx in original_window:
            measured_in_orig.append(meas)
            smoothed_in_orig.append(smoothed[i])

    surplus_smoothed = np.maximum(np.array(smoothed_in_orig) - measured_in_orig, 0)
    current_energy = np.sum(surplus_smoothed) * 5 / 60 / 10

    if current_energy > 0:
        scale_factor = target_discharge / current_energy
        scaled_adjusted = []
        for i, (idx, meas, _) in enumerate(idx_info):
            if idx in original_window:
                scaled = meas + (smoothed[i] - meas) * scale_factor
            else:
                scaled = smoothed[i]  # Keep smoothed values for extended points
            scaled_adjusted.append(scaled)
    else:
        scaled_adjusted = smoothed.copy()

    scaled_adjusted = np.clip(scaled_adjusted, 0, capacity_upper)

    # 4. Setup optimization model
    model = cp_model.CpModel()
    capacity_kw = int(capacity_upper * 1000)
    step_kw = int(max_step * 1000)
    target_power_gap = int(target_discharge * 120 * 1000)  # 5-min interval

    # Create variables for all extended points
    n = len(idx_info)
    pred_vars = [model.NewIntVar(0, capacity_kw, f"pred_{i}") for i in range(n)]
    surplus_vars = [model.NewIntVar(0, capacity_kw, f"surplus_{i}") for i in range(n)]

    # 4.1 Define surplus calculation
    for i, (idx, meas, _) in enumerate(idx_info):
        meas_kw = int(round(meas * 1000))
        diff = model.NewIntVar(-capacity_kw, capacity_kw, f"diff_{i}")
        model.Add(diff == pred_vars[i] - meas_kw)
        model.AddMaxEquality(surplus_vars[i], [diff, 0])

    # 4.2 Smoothing constraints between consecutive points
    for i in range(1, n):
        model.Add(pred_vars[i] - pred_vars[i-1] <= step_kw)
        model.Add(pred_vars[i-1] - pred_vars[i] <= step_kw)

    # 4.3 Boundary constraints with external points
    if extended_indices[0] > 0:
        left_neighbor = float(power_list[extended_indices[0]-1]["adjustedPower"])
        left_kw = int(round(left_neighbor * 1000))
        model.Add(pred_vars[0] - left_kw <= step_kw)
        model.Add(left_kw - pred_vars[0] <= step_kw)

    if extended_indices[-1] < len(power_list)-1:
        right_neighbor = float(power_list[extended_indices[-1]+1]["adjustedPower"])
        right_kw = int(round(right_neighbor * 1000))
        model.Add(pred_vars[-1] - right_kw <= step_kw)
        model.Add(right_kw - pred_vars[-1] <= step_kw)

    # 4.4 Discharge target constraint (only original window)
    original_surplus = [surplus_vars[i] for i in range(n) if idx_info[i][0] in original_window]
    model.Add(sum(original_surplus) == target_power_gap)

    # 4.5 Minimize deviation from smoothed curve
    deviations = []
    for i, target in enumerate(scaled_adjusted):
        target_kw = int(round(target * 1000))
        delta = model.NewIntVar(-capacity_kw, capacity_kw, f"delta_{i}")
        model.Add(delta == pred_vars[i] - target_kw)
        abs_delta = model.NewIntVar(0, capacity_kw, f"abs_delta_{i}")
        model.AddAbsEquality(abs_delta, delta)
        deviations.append(abs_delta)

    model.Minimize(sum(deviations))

    # 5. Solve and apply results
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10
    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError("优化失败，无可行解")

    # Update adjustedPower for extended window
    adjusted_results = {extended_indices[i]: solver.Value(pred_vars[i])/1000.0
                        for i in range(n)}

    # Apply to power_list
    for idx in adjusted_results:
        power_list[idx]["adjustedPower"] = f"{adjusted_results[idx]:.3f}"
        power_list[idx]["delta"] = f"{adjusted_results[idx] - float(power_list[idx]['predictPower']):+.3f}"

    # Verify discharge
    actual = get_discharge(power_list,
                           period_start.strftime("%Y-%m-%d %H:%M:%S"),
                           period_end.strftime("%Y-%m-%d %H:%M:%S"))
    if abs(actual - target_discharge) > 0.001:
        print(f"弃电量误差: {actual - target_discharge:.4f} 万kWh")

    return power_list


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
