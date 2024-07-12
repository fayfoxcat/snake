import os
import pandas as pd
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_folder(folder_path, station_list):
    def process_top_folder(top_folder):
        top_folder_path = os.path.join(folder_path, top_folder)
        result = []
        if station_list is not None and top_folder not in station_list:
            return result
        if os.path.isdir(top_folder_path) and not is_compressed_folder(top_folder):
            # 遍历每个日期文件夹
            for date_folder in os.listdir(top_folder_path):
                date_folder_path = os.path.join(top_folder_path, date_folder)
                if os.path.isdir(date_folder_path):
                    try:
                        # 日期文件夹的名称是 "YYYYMMDD" 格式
                        date = datetime.strptime(date_folder, "%Y%m%d")
                        expected_times = set()
                        # 生成当天每15分钟的时间戳
                        for i in range(96):  # 24小时，每小时4个15分钟的间隔
                            time_suffix = (date + timedelta(minutes=15 * i)).strftime("%H:%M")
                            expected_times.add(time_suffix)
                        # 实际路径文件列表
                        actual_files = set(os.listdir(date_folder_path))
                        actual_times = set()

                        # 提取实际文件中的时间部分
                        for file in actual_files:
                            if file.endswith("_CDQ.WPD"):
                                try:
                                    time_str = file.split('_')[2]
                                    time = datetime.strptime(time_str, "%H%M").strftime("%H:%M")
                                    actual_times.add(time)
                                except (IndexError, ValueError):
                                    continue

                        # 计算缺失的时间
                        missing_times = expected_times - actual_times
                        missing_times = sorted(list(missing_times))

                        # 将缺失时间合并成连续的时间段
                        missing_intervals = []
                        if missing_times:
                            start = missing_times[0]
                            end = missing_times[0]

                            for i in range(1, len(missing_times)):
                                current_time = datetime.strptime(missing_times[i], "%H:%M")
                                previous_time = datetime.strptime(missing_times[i - 1], "%H:%M")

                                if current_time - previous_time == timedelta(minutes=15):
                                    end = missing_times[i]
                                else:
                                    missing_intervals.append(f"{start} - {end}" if start != end else start)
                                    start = missing_times[i]
                                    end = missing_times[i]

                            missing_intervals.append(f"{start} - {end}" if start != end else start)

                        missing_count = len(missing_times)

                        # 如果有缺失文件，添加到结果列表
                        if missing_count > 0:
                            result.append({
                                "场站": top_folder,
                                "日期": date_folder,
                                "缺失数量": missing_count,
                                "缺失时间": ", ".join(missing_intervals)
                            })
                    except ValueError:
                        # 如果日期文件夹名称不符合预期的日期格式，跳过该文件夹
                        print(f"跳过不符合日期格式的文件夹: {date_folder}")
        return result

    # 初始化列表，用于存储结果
    results = []

    # 使用 ThreadPoolExecutor 并行处理顶级文件夹
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_top_folder, top_folder): top_folder for top_folder in os.listdir(folder_path)}
        for future in as_completed(futures):
            top_folder = futures[future]
            try:
                results.extend(future.result())
            except Exception as exc:
                print(f"{top_folder} 生成异常: {exc}")

    # 将结果转换为DataFrame
    results_df = pd.DataFrame(results)

    # 按场站和日期排序
    results_df.sort_values(by=['场站', '日期'], inplace=True)

    # 去重
    results_df.drop_duplicates(inplace=True)

    # 将结果写入Excel文件
    results_df.to_excel(r"缺失报告.xlsx", index=False)
    print("处理完成，结果已保存至：" + os.path.dirname(os.path.realpath(__file__)) + "\缺失报告.xlsx'")

def is_compressed_folder(folder_name):
    # 通过文件扩展名判断是否为压缩文件夹
    compressed_extensions = ['.zip', '.rar', '.7z', '.tar', '.gz']
    return any(folder_name.endswith(ext) for ext in compressed_extensions)

# 目标目录
base_dir = r"C:\Users\root\Desktop\2023年3月\fileData"
statistics_list_3 = ['GHSYFD', 'GXHHFD', 'GXLHFD', 'GXRHFD', 'SFGYFD', 'SNBYJF', 'SNLSFD', 'SNSYHF', 'SCTHFD', 'GYFDFX',
                     'JSHRFD', 'HNRHFD', 'HRTHFD', 'HZSYFD', 'RBDLQF', 'XTGYFD', 'SXFHFD', 'ZDDYFD', 'ZDCJGF', 'BHFDBT',
                     'JSXSFD', 'CJXHFD', 'YNSHFD', 'GYFDFY', 'XXFNFD', 'SXSHGF', 'RNHAFD', 'GXDZFD', 'GRJHFD', 'GXGYFD',
                     'HNJHFD', 'HZHYFD', 'XXSHFD', 'GHRHFD']

process_folder(base_dir, None)
