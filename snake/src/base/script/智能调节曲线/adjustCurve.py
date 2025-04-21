#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
功率预测‑调节一体化脚本
==================================================
包含：
1. LOWESS 平滑
2. CP‑SAT 优化调节
3. 弃电量计算
4. 交互式曲线绘制
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates
from matplotlib.backend_bases import MouseEvent
from matplotlib.ticker import FuncFormatter
from ortools.sat.python import cp_model
from statsmodels.nonparametric.smoothers_lowess import lowess

# ================ 全局常量 ================
TIME_FMT: str = "%Y-%m-%d %H:%M:%S"

plt.rcParams.update({
    "font.sans-serif": ["SimHei"],
    "axes.unicode_minus": False,
    "font.size": 14,
    "lines.linewidth": 2,
})


# ================ 工具函数 ================
def str2dt(ts: str) -> datetime:
    """时间字符串 &rarr; datetime"""
    return datetime.strptime(ts, TIME_FMT)


# ================ 可视化 ================
def plot_power_curves(items, title='功率测量与预测', figsize=(60, 20)):
    # ---------- 1. 解析数据 ----------
    times = [datetime.strptime(i["timePoint"], "%Y-%m-%d %H:%M:%S") for i in items]
    measured = [float(i["measuredPower"]) for i in items]
    predicted = [float(i["predictPower"]) for i in items]
    first_adj = [float(i["adjustedPowerFirst"]) for i in items] if "adjustedPowerFirst" in items[0] else None
    final_adj = [float(i["adjustedPower"]) for i in items] if "adjustedPower" in items[0] else None

    # ---------- 2. 作图 ----------
    fig, ax = plt.subplots(figsize=figsize, dpi=100)
    plt.rcParams.update({'font.size': 26, 'lines.linewidth': 3})

    ax.plot(times, measured, label='实际出力', marker='o', color='orange', markersize=8)
    ax.plot(times, predicted, label='预测功率', marker='o', color='grey', markersize=8, alpha=0.5)
    if first_adj: ax.plot(times, first_adj, label='初次调节预测功率', marker='o', color='green', markersize=8,
                          alpha=0.5)
    if final_adj: ax.plot(times, final_adj, label='最终调节预测功率', marker='o', color='blue', markersize=8, alpha=0.5)

    # ---------- 3. 让横坐标“每个点都画” ----------
    stride = 3 # 每隔一个点(即显示 0,2,4,6… 索引对应的时间)
    ax.set_xticks(times[::stride])
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    fig.autofmt_xdate(rotation=45, ha='right')

    # ---------- 4. 其余美化 ----------
    ax.set_title(title, fontsize=30, pad=20)
    ax.set_xlabel('时间', fontsize=26)
    ax.set_ylabel('功率 (MW)', fontsize=26)
    ax.legend(fontsize=26)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.2f}'))

    # ---------- 5. 修复 on_move ----------
    def on_move(event: MouseEvent):
        """鼠标移动时动态更新副标题。"""
        if event.inaxes is not ax or event.xdata is None or event.ydata is None:
            return
        # 这里直接用 mdates，不要把它作为参数传进来，否则会被 None 覆盖
        x_dt = mdates.num2date(event.xdata)
        ax.set_title(
            f"{title}\n时间: {x_dt:%Y-%m-%d %H:%M:%S} | 功率: {event.ydata:.2f}",
            fontsize=30, pad=20
        )
        fig.canvas.draw_idle()

    # 连接事件
    fig.canvas.mpl_connect('motion_notify_event', on_move)

    plt.tight_layout()
    plt.show(block=True)


# ================ 核心算法 ================
def apply_lowess_smoothing(predictions: list[float], frac: float = 0.2, it: int = 3) -> np.ndarray:
    """LOWESS 平滑"""
    x = np.arange(len(predictions))
    return lowess(predictions, x, frac=frac, it=it, return_sorted=False)


def get_discharge(items: List[Dict[str, str]],
                  start_time: str, end_time: str) -> float:
    """
    计算指定时间段弃电量（万 kWh）
    公式：max(预测‑实际, 0) &times; 5 分钟 / 60 / 10
    """
    s_dt, e_dt = map(str2dt, (start_time, end_time))
    total = sum(
        max(float(e.get("adjustedPower", e["predictPower"]))
            - float(e["measuredPower"]), 0)
        * 5 / 60 / 10
        for e in items if s_dt <= str2dt(e["timePoint"]) <= e_dt
    )
    return total


def smart_adjust(
        power_list: List[Dict[str, str]],
        period_start: str,
        period_end: str,
        target_discharge: float,
        capacity_upper: float,
        *,
        max_step: float = 4.0,
        lowess_frac: float = 0.1,
        lowess_it: int = 1,
        extend_by: int = 12,
) -> List[Dict[str, str]]:
    """
    OR‑Tools CP‑SAT 智能调节

    Parameters
    ----------
    power_list : List[Dict]
        原始功率数据（函数会原地更新 adjustedPower）
    period_start, period_end : str
        目标弃电时间窗口
    target_discharge : float
        目标弃电量（万 kWh）
    capacity_upper : float
        机组容量上限 (MW)
    Other Keyword Args
    ------------------
    max_step : float
        相邻 5min 点允许的最大变化 (MW)
    lowess_frac : float
        LOWESS 平滑窗口比例
    lowess_it : int
        LOWESS 迭代次数
    extend_by : int
        在窗口两侧额外扩展的采样点数
    """
    # ---------- 0. 准备 ----------
    period_start_dt, period_end_dt = map(str2dt, (period_start, period_end))
    for item in power_list:
        item.setdefault("adjustedPower", item["predictPower"])

    all_times = [str2dt(i["timePoint"]) for i in power_list]
    window_idx = [i for i, t in enumerate(all_times) if period_start_dt <= t <= period_end_dt]
    if not window_idx:
        raise ValueError("时间窗口与数据不匹配")

    ext_idx = list(range(max(0, min(window_idx) - extend_by), min(len(power_list) - 1, max(window_idx) + extend_by) + 1))
    window_set = set(window_idx)

    idx_info = [(idx, float(power_list[idx]["measuredPower"]), float(power_list[idx]["adjustedPower"])) for idx in ext_idx]

    # ---------- 1. LOWESS 平滑 ----------
    smoothed = apply_lowess_smoothing( [orig for _, _, orig in idx_info], frac=lowess_frac, it=lowess_it)

    # ---------- 2. 比例缩放满足目标弃电 ----------
    meas_orig = np.array([meas for (idx, meas, _), s in zip(idx_info, smoothed) if idx in window_set])
    smooth_orig = np.array([s for (idx, _, _), s in zip(idx_info, smoothed) if idx in window_set])
    surplus = np.maximum(smooth_orig - meas_orig, 0)
    cur_energy = surplus.sum() * 5 / 60 / 10
    scale = 1.0 if cur_energy == 0 else target_discharge / cur_energy

    scaled_adj = [(meas + (smt - meas) * scale if idx in window_set else smt) for (idx, meas, _), smt in zip(idx_info, smoothed)]
    scaled_adj = np.clip(scaled_adj, 0, capacity_upper)

    # ---------- 3. 构建 CP‑SAT ----------
    model = cp_model.CpModel()
    cap_kw = int(capacity_upper * 1000)
    step_kw = int(max_step * 1000)
    target_kw_gap = int(target_discharge * 120 * 1000)  # 5min

    n = len(idx_info)
    pred = [model.NewIntVar(0, cap_kw, f"pred_{i}") for i in range(n)]
    surplus_v = [model.NewIntVar(0, cap_kw, f"surp_{i}") for i in range(n)]

    # 3.1 差额与弃电
    for i, (_, meas, _) in enumerate(idx_info):
        meas_kw = int(round(meas * 1000))
        diff = model.NewIntVar(-cap_kw, cap_kw, f"diff_{i}")
        model.Add(diff == pred[i] - meas_kw)
        model.AddMaxEquality(surplus_v[i], [diff, 0])

    # 3.2 平滑约束
    for i in range(1, n):
        model.Add(pred[i] - pred[i - 1] <= step_kw)
        model.Add(pred[i - 1] - pred[i] <= step_kw)

    # 3.3 边界约束
    if ext_idx[0] > 0:
        left_kw = int(round(float(power_list[ext_idx[0] - 1]["adjustedPower"]) * 1000))
        model.Add(pred[0] - left_kw <= step_kw)
        model.Add(left_kw - pred[0] <= step_kw)
    if ext_idx[-1] < len(power_list) - 1:
        right_kw = int(round(float(power_list[ext_idx[-1] + 1]["adjustedPower"]) * 1000))
        model.Add(pred[-1] - right_kw <= step_kw)
        model.Add(right_kw - pred[-1] <= step_kw)

    # 3.4 目标弃电量
    model.Add(sum(surplus_v[i] for i, (idx, _, _) in enumerate(idx_info) if idx in window_set) == target_kw_gap)

    # 3.5 目标函数：逼近缩放曲线
    dev = []
    for i, tgt in enumerate(scaled_adj):
        tgt_kw = int(round(tgt * 1000))
        delta = model.NewIntVar(-cap_kw, cap_kw, f"delta_{i}")
        model.Add(delta == pred[i] - tgt_kw)
        abs_delta = model.NewIntVar(0, cap_kw, f"abs_{i}")
        model.AddAbsEquality(abs_delta, delta)
        dev.append(abs_delta)
    model.Minimize(sum(dev))

    # ---------- 4. 求解 ----------
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10
    status = solver.Solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError("优化失败：无可行解")

    # ---------- 5. 写回结果 ----------
    for i, idx in enumerate(ext_idx):
        new_val = solver.Value(pred[i]) / 1000
        power_list[idx]["adjustedPower"] = f"{new_val:.3f}"
        diff = new_val - float(power_list[idx]["predictPower"])
        power_list[idx]["delta"] = f"{diff:+.3f}"

    # ---------- 6. 校验 ----------
    actual = get_discharge(power_list, period_start, period_end)
    if abs(actual - target_discharge) > 0.001:
        print(f"警告：弃电量偏差 {actual - target_discharge:.4f} 万kWh")

    return power_list


# ================ 入口函数 ================
def main() -> None:
    capacity = 50.0  # 单位 MW
    target_base = 5.5820  # 万 kWh
    start_time = "2025-04-16 07:00:00"
    end_time = "2025-04-16 17:00:00"

    data_path = Path(__file__).with_name("data.json")
    with data_path.open(encoding="utf-8") as fp:
        data: List[Dict[str, str]] = json.load(fp)

    print("调整前弃电量:",
          f"{get_discharge(data, start_time, end_time):.4f} 万kWh")

    for i in range(10):
        target = target_base + 2 * i
        # 第一次粗调
        adjusted = smart_adjust(
            data, start_time, end_time, target, capacity,
            max_step=2.0, lowess_frac=0.3, lowess_it=2)
        for item in adjusted:
            item["adjustedPowerFirst"] = item["adjustedPower"]
        # 第二次精调
        adjusted = smart_adjust(
            adjusted, start_time, end_time, target, capacity, max_step=2.0)

        print("调整后弃电量:",
              f"{get_discharge(adjusted, start_time, end_time):.4f} 万kWh")
        plot_power_curves(adjusted,
                          title=f"目标弃电量 {target:.2f} 万kWh")


if __name__ == "__main__":
    main()
