import json
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.backend_bases import MouseEvent
from matplotlib.ticker import FuncFormatter
from ortools.sat.python import cp_model

# ---------- Matplotlib 中文与外观 ----------
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def plot_power_curves(items, title='功率测量与预测', figsize=(60, 20)):
    times = [datetime.strptime(i["timePoint"], "%Y-%m-%d %H:%M:%S") for i in items]
    measured = [float(i["measuredPower"]) for i in items]
    predicted = [float(i["predictPower"]) for i in items]

    fig, ax = plt.subplots(figsize=figsize, dpi=100)
    plt.rcParams.update({'font.size': 26, 'lines.linewidth': 3})
    ax.plot(times, measured, label='实际出力', marker='o', color='green', markersize=8)
    ax.plot(times, predicted, label='可用功率', marker='o', color='red', markersize=8)

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


# ---------- 智能调节 ----------
def smart_adjust(
        items, start_dt, end_dt, target_discharge, capacity,
        max_step=2.0, smooth_weight=1.0, curvature_weight=1.0, energy_tol=1e-6
):
    """窗口内调 predictPower，使弃电量精准匹配且曲线平滑。"""
    start_dt, end_dt = [datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                        for t in (start_dt, end_dt)]

    # 1. 收集窗口内点
    idx_info = [(idx,
                 float(it["measuredPower"]),
                 float(it["predictPower"]))
                for idx, it in enumerate(items)
                if start_dt <= datetime.strptime(it["timePoint"], "%Y-%m-%d %H:%M:%S") <= end_dt]
    if not idx_info:
        raise ValueError("时间窗口与数据不匹配。")

    n = len(idx_info)
    cap_kW  = int(round(capacity * 1000))
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
        m.Add(pred[i] - pred[i-1] <= step_kW)
        m.Add(pred[i-1] - pred[i] <= step_kW)

    # 3.1 平滑约束 (窗口边界&hArr;原曲线)
    first_idx, last_idx = idx_info[0][0], idx_info[-1][0]

    if first_idx > 0:                       # 左边还有点
        orig_prev = float(items[first_idx - 1]["predictPower"])
        orig_prev_kW = int(round(orig_prev * 1000))
        m.Add(pred[0] - orig_prev_kW <= step_kW)
        m.Add(orig_prev_kW - pred[0] <= step_kW)

    if last_idx < len(items) - 1:           # 右边还有点
        orig_next = float(items[last_idx + 1]["predictPower"])
        orig_next_kW = int(round(orig_next * 1000))
        m.Add(pred[-1] - orig_next_kW <= step_kW)
        m.Add(orig_next_kW - pred[-1] <= step_kW)

    # 4. 弃电量等式
    m.Add(sum(surplus) == energy_target_kW5min)

    # 5. 目标：|Δ| + smooth1 + smooth2
    abs_delta, abs_slope, abs_curve = [], [], []
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

        if i:  # 一阶斜率
            s = m.NewIntVar(-cap_kW, cap_kW, f"s_{i}")
            m.Add(s == pred[i] - pred[i-1])
            su = m.NewIntVar(0, cap_kW, f"su_{i}")
            sv = m.NewIntVar(0, cap_kW, f"sv_{i}")
            m.Add(s == su - sv)
            m.Add(s >= -su)
            m.Add(s <= sv)
            abs_slope.append(su + sv)

        if 0 < i < n-1:  # 二阶曲率
            c = m.NewIntVar(-cap_kW, cap_kW, f"c_{i}")
            m.Add(c == pred[i+1] - 2*pred[i] + pred[i-1])
            cu = m.NewIntVar(0, cap_kW, f"cu_{i}")
            cv = m.NewIntVar(0, cap_kW, f"cv_{i}")
            m.Add(c == cu - cv)
            m.Add(c >= -cu)
            m.Add(c <= cv)
            abs_curve.append(cu + cv)

    m.Minimize(
        sum(abs_delta) +
        smooth_weight * sum(abs_slope) +
        curvature_weight * sum(abs_curve)
    )

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60
    solver.parameters.num_search_workers = 8
    if solver.Solve(m) not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError("求解失败：无可行解。")

    # 6. 写回结果
    idx2newpred = {idx: solver.Value(pred[i]) / 1000.0
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

    # 7. 精度检查
    actual = get_discharge(new_items, start_dt.strftime("%Y-%m-%d %H:%M:%S"),
                           end_dt.strftime("%Y-%m-%d %H:%M:%S"))
    if abs(actual - target_discharge) > energy_tol:
        raise RuntimeError(
            f"弃电量 {actual:.6f} 万kWh &ne; 目标 {target_discharge:.6f}")

    return new_items


# ---------- 直接运行 ----------
if __name__ == "__main__":
    capacity = 50.0
    targetDischarge = 30          # 万kWh
    startTime = "2025-04-16 07:00:00"
    endTime   = "2025-04-16 17:00:00"

    with open("data.json", encoding="utf-8") as f:
        data = json.load(f)

    print("调整前弃电量:",
          f"{get_discharge(data, startTime, endTime):.4f} 万kWh")

    adjusted = smart_adjust(
        data, startTime, endTime, targetDischarge, capacity,
        max_step=2.0, smooth_weight=1.0, curvature_weight=1.5
    )

    print("调整后弃电量:",
          f"{get_discharge(adjusted, startTime, endTime):.4f} 万kWh")

    # 如果需要可视化
    plot_power_curves(adjusted)