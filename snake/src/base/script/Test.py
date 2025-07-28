from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd

# 定义季节判断函数（气象学季节）
def get_season(month):
    if 3 <= month <= 5: return "春季"
    elif 6 <= month <= 8: return "夏季"
    elif 9 <= month <= 11: return "秋季"
    else: return "冬季"  # 12月及1-2月

# 原始时间段数据（已处理换行和空格）
time_periods = [
    "2024-01-22 04:08~2024-01-22 05:29","2024-01-23 11:20~2024-01-23 15:15","2024-02-05 12:26~2024-02-05 14:05","2024-02-08 12:31~2024-02-08 14:21","2024-02-08 14:36~2024-02-08 15:26","2024-02-12 09:29~2024-02-12 16:10","2024-02-12 16:22~2024-02-12 16:54","2024-02-12 17:44~2024-02-12 19:11","2024-02-12 19:46~2024-02-12 21:11","2024-02-13 02:07~2024-02-13 02:27","2024-02-13 02:50~2024-02-13 03:09","2024-02-13 05:38~2024-02-13 06:42","2024-02-13 08:03~2024-02-13 11:19","2024-02-13 11:37~2024-02-13 12:12","2024-02-15 06:22~2024-02-15 09:32","2024-02-18 04:34~2024-02-18 05:11","2024-02-18 05:20~2024-02-18 06:59","2024-02-26 12:40~2024-02-26 12:44","2024-02-26 12:55~2024-02-26 14:14","2024-03-12 13:16~2024-03-12 14:40","2024-03-12 15:01~2024-03-12 15:19","2024-03-17 12:51~2024-03-17 16:00","2024-03-19 12:39~2024-03-19 14:02","2024-03-20 11:36~2024-03-20 12:38","2024-03-20 12:47~2024-03-20 12:59","2024-03-21 12:29~2024-03-21 14:07","2024-03-22 11:28~2024-03-22 13:50","2024-04-01 13:18~2024-04-01 14:07","2024-04-04 10:45~2024-04-04 12:30","2024-04-10 11:17~2024-04-10 15:32","2024-04-19 10:54~2024-04-19 12:41","2024-04-20 12:58~2024-04-20 14:23","2024-04-25 12:49~2024-04-25 14:06","2024-04-26 12:26~2024-04-26 14:35","2024-04-29 11:24~2024-04-29 13:57","2024-05-01 09:15~2024-05-01 09:43","2024-05-01 11:53~2024-05-01 13:04","2024-05-01 13:15~2024-05-01 14:20","2024-05-10 12:01~2024-05-10 14:32","2024-05-16 09:32~2024-05-16 10:33","2024-05-16 10:41~2024-05-16 12:06","2024-05-18 11:15~2024-05-18 12:38","2024-09-22 08:27~2024-09-22 10:22","2024-09-22 13:29~2024-09-22 15:23","2024-10-02 11:55~2024-10-02 12:25","2024-11-27 12:06~2024-11-27 15:02","2024-12-28 11:42~2024-12-28 13:07","2025-01-22 13:25~2025-01-22 15:13","2025-01-27 08:02~2025-01-27 16:24","2025-01-28 09:01~2025-01-28 10:15","2025-01-28 11:35~2025-01-28 13:00","2025-01-28 13:05~2025-01-28 14:30","2025-01-30 08:31~2025-01-30 16:43","2025-02-03 12:29~2025-02-03 13:53","2025-02-05 11:29~2025-02-05 13:25","2025-02-19 12:03~2025-02-19 14:06"
]

# 初始化统计字典
season_hours = defaultdict(float)
month_hours = defaultdict(float)
hour_hours = defaultdict(float)

# 处理每个时间段
for period in time_periods:
    start_str, end_str = period.strip().split("~")
    start = datetime.strptime(start_str.strip(), "%Y-%m-%d %H:%M")
    end = datetime.strptime(end_str.strip(), "%Y-%m-%d %H:%M")

    current = start
    while current < end:
        # 计算当前小时结束时间
        hour_end = (current + timedelta(hours=1)).replace(minute=0, second=0)
        chunk_end = min(hour_end, end)

        # 计算当前小时内的持续时间（精确到分钟）
        duration = (chunk_end - current).total_seconds() / 3600

        # 统计季节和月份（根据实际发生时间）
        season = get_season(current.month)
        season_hours[season] += duration
        month_hours[current.month] += duration

        # 统计小时段（如12点指12:00-13:00）
        hour_hours[current.hour] += duration

        current = chunk_end  # 移动到下一个小时

# 生成统计结果
def get_max(data_dict):
    max_key = max(data_dict, key=lambda k: data_dict[k])
    return max_key, data_dict[max_key]

# 输出详细统计
print("季节统计（小时）:")
for season, hours in sorted(season_hours.items(), key=lambda x: x):
    print(f"{season}: {hours:.2f}h")

print("\n月份统计（小时）:")
for month, hours in sorted(month_hours.items(), key=lambda x: x):
    print(f"{month}月: {hours:.2f}h")

print("\n小时段统计（小时）:")
for hour, hours in sorted(hour_hours.items(), key=lambda x: x):
    print(f"{hour:02d}:00-{hour+1:02d}:00: {hours:.2f}h")

# 获取最大值
max_season, season_h = get_max(season_hours)
max_month, month_h = get_max(month_hours)
max_hour, hour_h = get_max(hour_hours)

print(f"\n分析结果：")
print(f"弃电最严重季节：{max_season}（{season_h:.2f}小时）")
print(f"弃电最严重月份：{max_month}月（{month_h:.2f}小时）")
print(f"弃电最严重时段：{max_hour:02d}:00-{max_hour+1:02d}:00（{hour_h:.2f}小时）")
