import os
import pandas as pd
from datetime import datetime, timedelta

# 目标目录
base_dir = r"C:\Users\root\Desktop\cdq202301_new"

# 初始化列表，用于存储结果
results = []

# 遍历每个顶级文件夹
for top_folder in os.listdir(base_dir):
    top_folder_path = os.path.join(base_dir, top_folder)
    if os.path.isdir(top_folder_path):
        # 遍历每个日期文件夹
        for date_folder in os.listdir(top_folder_path):
            date_folder_path = os.path.join(top_folder_path, date_folder)
            if os.path.isdir(date_folder_path):
                try:
                    # 假设日期文件夹的名称是 "YYYYMMDD" 格式
                    date = datetime.strptime(date_folder, "%Y%m%d")
                    expected_files = set()

                    # 生成当天每15分钟的时间戳
                    for i in range(96):  # 24小时，每小时4个15分钟的间隔
                        time_suffix = (date + timedelta(minutes=15 * i)).strftime("%H%M")
                        expected_file = f"{top_folder}_{date_folder}_{time_suffix}_CDQ.WPD"
                        expected_files.add(expected_file)

                    actual_files = set(os.listdir(date_folder_path))

                    # 计算缺失的文件
                    missing_files = expected_files - actual_files
                    missing_count = len(missing_files)

                    # 如果有缺失文件，添加到结果列表
                    if missing_count > 0:
                        results.append({
                            "场站": top_folder,
                            "日期": date_folder,
                            "缺失数量": missing_count,
                            "缺失文件": ", ".join(sorted(missing_files))
                        })
                except ValueError:
                    # 如果日期文件夹名称不符合预期的日期格式，跳过该文件夹
                    print(f"跳过不符合日期格式的文件夹: {date_folder}")

# 将结果转换为DataFrame
results_df = pd.DataFrame(results)

# 将结果写入Excel文件
results_df.to_excel(r"C:\Users\root\Desktop\missing_files_report.xlsx", index=False)

print("Report generated successfully.")
