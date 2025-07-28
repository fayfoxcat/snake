import os
import json
import requests
from datetime import datetime, timedelta
from collections import defaultdict
import shutil
import threading
import queue
from concurrent.futures import ThreadPoolExecutor

# 配置信息
CONFIG = {
    "system1_url": "http://172.18.31.3:8096/elss-web/api/analyze/distribution-overview",
    "system2_url": "http://172.18.37.248:30004/elss-web/api/analyze/distribution-overview",
    "access_token": "ZXlKMGVYQWlPaUpLVjFRaUxDSmhiR2NpT2lKSVV6STFOaUo5LmV5SjFjMlZ5U1dRaU9qRXNJblZ6WlhKdVlXMWxJam9pWVdSdGFXNGlmUS40YW45TjhNWmRaZEdrYm5CdlY5MjRZdmNONm5EVHRCX2t4S3MzQlV2NmFF",
    "output_dir1": "旧版本",
    "output_dir2": "新版本",
    "diff_dir": "差异文件",
    "start_date": "2025-01-01",
    "end_date": "2025-05-30",
    "max_workers": 4,  # 线程池大小
    "request_payload": {
        "startDate": "2025-04-08",
        "endDate": "2025-04-08",
        "stationIds": ["102000008", "102000009", "102000010", "102000011", "102000012", "102000013", "102000014",
                       "102000015", "102000016", "102000017", "102000026", "102000027", "102000028", "102000029",
                       "102000030", "102000031", "102000032", "102000033", "102000034", "102000035", "102000036",
                       "102000037", "102000038", "102000040", "102000041", "102000042", "102000043", "102000044",
                       "102000045", "102000046", "102000047", "102000048", "102000049", "102000050", "102000051",
                       "102000052", "102000053", "102000054", "102000055", "102000056", "102000057", "102000058",
                       "102000059", "102000060", "102000061", "102000062", "102000063", "102000064", "102000065",
                       "102000066", "102000067", "102000068", "102000069", "102000070", "102000071", "102000072",
                       "102000073", "102000074", "102000185", "102000186", "102000205", "102000206", "102000207",
                       "102000226", "102000228", "102000229", "102000230", "102000245", "102000252", "102000265",
                       "102000266", "102000285", "102000286", "102000287", "102000305", "102000306", "102000307",
                       "102000308", "102000325", "102000326", "102000327", "102000328", "102000329", "102000330",
                       "102000331", "102000333", "102000334", "102000335", "102000336", "102000337", "102000338",
                       "102000339", "102000340", "102000341", "102000342", "102000343", "102000344", "102000345",
                       "102000346", "102000347", "102000348", "102000349", "102000350", "102000351", "102000352",
                       "102000353", "102000354", "102000355", "102000356", "102000357", "102000358", "102000359",
                       "102000360", "102000361", "102000362", "102000363", "102000364", "102000365", "102000366",
                       "102000367", "102000368", "102000369", "102000370", "102000371", "102000372", "102000373",
                       "102000374", "102000375", "102000376", "102000377", "102000378", "102000379", "102000380",
                       "102000381", "102000382", "102000383", "102000384", "102000385", "102000386", "102000387",
                       "102000388", "102000389", "102000390", "102000391", "102000392", "102000393", "102000394",
                       "102000395", "102000396", "102000397", "102000398", "102000399", "102000400", "102000401",
                       "102000402", "102000403", "102000404", "102000405", "102000406", "102000407", "102000408",
                       "102000409", "102000410", "102000411", "102000412", "102000413", "102000414", "102000415",
                       "102000416", "102000417", "102000418", "102000419", "102000420", "102000421", "102000422",
                       "102000423", "102000424", "102000425", "102000426", "102000427", "102000428", "102000429",
                       "102000430", "102000431", "102000432", "102000433", "102000434", "102000435", "102000436",
                       "102000437", "102000438", "102000439", "102000441", "102000442", "102000443", "102000444",
                       "102000445", "102000446", "102000447", "102000448", "102000449", "102000500", "102000501",
                       "102000502", "102000503", "102000504", "102000505", "102000506", "102000507", "102000508",
                       "102000509", "102000510", "102000511", "102000512", "102000513", "102000515", "102000516",
                       "102000517", "102000518", "102000519", "102000520", "102000521", "102000522", "102000523",
                       "102000524", "102000525", "102000526", "102000527", "102000528", "102000529", "102000530",
                       "102000531", "102000532", "102000533", "102000534", "103000001", "200000000", "200000011",
                       "200000015", "200000016", "200000017", "200000018", "200000019", "200000020", "200000021",
                       "200000022", "200000023", "200000024", "200000025", "200000026", "200000027", "200000028",
                       "200000029", "200000030", "200000031", "200000032", "200000033", "200000034", "200000035",
                       "200000036", "200000037", "200000038", "200000039", "200000040", "200000041", "200000042",
                       "200000043", "200000044", "200000045", "200000046", "200000047", "200000048", "200000049",
                       "200000050", "200000051", "200000052", "200000053", "200000054", "200000055", "200000056",
                       "200000057"
                       ],
        "dischargeTypes": [
            "DISCHARGE_SPECIAL_TYPE",
            "DISCHARGE_MANUAL_SPECIAL_TYPE"
        ],
        "verificationConditions": [
            "DISCHARGE_VC_SWITCH_AGC",
            "DISCHARGE_VC_AVAILABLE_AGC",
            "DISCHARGE_VC_GRID_OR_QUALIFIED"
        ],
        "sortMap": {},
        "replaceAvaPower": False
    }
}

# 全局队列用于存储待比较的文件对
file_pair_queue = queue.Queue()
# 用于存储比较结果
comparison_results = []
# 用于同步文件写入
file_write_lock = threading.Lock()


def setup_directories():
    """创建输出目录"""
    os.makedirs(CONFIG["output_dir1"], exist_ok=True)
    os.makedirs(CONFIG["output_dir2"], exist_ok=True)
    os.makedirs(CONFIG["diff_dir"], exist_ok=True)


def make_request(url, payload, access_token):
    """发送POST请求"""
    headers = {
        "access-token": access_token,
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None


def save_response(data, directory, date):
    """保存响应到文件"""
    filename = os.path.join(directory, f"response_{date}.json")
    with file_write_lock:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"已保存: {filename}")
    return filename


def fetch_single_date(date_str, payload):
    """获取单个日期的数据"""
    print(f"\n处理日期: {date_str}")

    # 更新请求payload中的日期
    current_payload = payload.copy()
    current_payload["startDate"] = date_str
    current_payload["endDate"] = date_str

    # 并行请求两个系统
    with ThreadPoolExecutor(max_workers=2) as executor:
        future1 = executor.submit(make_request, CONFIG["system1_url"], current_payload, CONFIG["access_token"])
        future2 = executor.submit(make_request, CONFIG["system2_url"], current_payload, CONFIG["access_token"])

        response1 = future1.result()
        response2 = future2.result()

    # 保存响应并放入队列
    if response1 and response2:
        file1 = save_response(response1, CONFIG["output_dir1"], date_str)
        file2 = save_response(response2, CONFIG["output_dir2"], date_str)
        file_pair_queue.put((file1, file2, date_str))


def fetch_data_for_dates():
    """按日期范围获取数据，使用线程池"""
    start_date = datetime.strptime(CONFIG["start_date"], "%Y-%m-%d")
    end_date = datetime.strptime(CONFIG["end_date"], "%Y-%m-%d")

    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)

    # 使用线程池并行处理日期
    with ThreadPoolExecutor(max_workers=CONFIG["max_workers"]) as executor:
        for date_str in dates:
            executor.submit(fetch_single_date, date_str, CONFIG["request_payload"])


def compare_files_worker():
    """工作线程，从队列中获取文件对进行比较"""
    while True:
        try:
            file1, file2, date_str = file_pair_queue.get(timeout=10)  # 10秒超时

            match, summary, details = compare_files(file1, file2)
            if not match:
                comparison_results.append((date_str, summary, details))
                print(f"差异发现于: {date_str}")
                copy_diff_files(file1, file2, f"response_{date_str}.json")

            file_pair_queue.task_done()
        except queue.Empty:
            break


def compare_files(file1, file2):
    """比较两个文件内容"""
    with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
        data1 = json.load(f1)
        data2 = json.load(f2)

        if data1 == data2:
            return True, None, None

        # 找出具体差异
        diff_details = {}
        diff_summary = defaultdict(int)

        for key in set(data1.keys()).union(data2.keys()):
            if key not in data1:
                diff_details[key] = {"system1": "缺失", "system2": data2[key]}
                diff_summary["字段缺失"] += 1
            elif key not in data2:
                diff_details[key] = {"system1": data1[key], "system2": "缺失"}
                diff_summary["字段缺失"] += 1
            elif data1[key] != data2[key]:
                diff_details[key] = {"system1": data1[key], "system2": data2[key]}
                if isinstance(data1[key], (dict, list)):
                    diff_summary["复杂类型差异"] += 1
                else:
                    diff_summary["简单类型差异"] += 1

        return False, dict(diff_summary), diff_details


def copy_diff_files(file1, file2, filename):
    """将有差异的文件复制到差异目录"""
    diff_dir1 = os.path.join(CONFIG["diff_dir"], CONFIG["output_dir1"])
    diff_dir2 = os.path.join(CONFIG["diff_dir"], CONFIG["output_dir2"])

    os.makedirs(diff_dir1, exist_ok=True)
    os.makedirs(diff_dir2, exist_ok=True)

    shutil.copy2(file1, os.path.join(diff_dir1, filename))
    shutil.copy2(file2, os.path.join(diff_dir2, filename))
    print(f"已复制差异文件到: {diff_dir1} 和 {diff_dir2}")


def generate_reports():
    """生成比较结果报告"""
    if not comparison_results:
        print("所有文件内容一致")
        return

    # 按日期排序结果
    comparison_results.sort(key=lambda x: x[0])

    # 准备报告数据
    summary_report = {result[0]: result[1] for result in comparison_results}
    detailed_report = {result[0]: result[2] for result in comparison_results}

    # 保存摘要报告
    summary_file = os.path.join(CONFIG["diff_dir"], "diff_summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary_report, f, ensure_ascii=False, indent=2)
    print(f"\n差异摘要已保存到: {summary_file}")

    # 打印摘要报告
    print("\n=== 差异摘要 ===")
    for date_str, summary in summary_report.items():
        print(f"\n日期: {date_str}")
        for diff_type, count in summary.items():
            print(f"{diff_type}: {count}处")

    # 保存详细报告
    detailed_file = os.path.join(CONFIG["diff_dir"], "diff_details.json")
    with open(detailed_file, 'w', encoding='utf-8') as f:
        json.dump(detailed_report, f, ensure_ascii=False, indent=2)
    print(f"\n详细差异已保存到: {detailed_file}")

    # 生成建议
    generate_suggestions(summary_report, detailed_report)


def generate_suggestions(summary_report, detailed_report):
    """根据差异生成建议"""
    print("\n=== 差异分析建议 ===")

    # 总体建议
    total_files = len(summary_report)
    total_diffs = sum(sum(summary.values()) for summary in summary_report.values())
    print(f"\n共发现 {total_files} 个文件存在差异，总计 {total_diffs} 处不同")

    # 按文件给出建议
    for date_str, summary in summary_report.items():
        print(f"\n日期: {date_str}")
        print(f"差异类型统计: {json.dumps(summary, indent=2, ensure_ascii=False)}")

        # 获取前3个差异字段作为示例
        sample_diffs = list(detailed_report[date_str].items())[:3]
        print("\n示例差异:")
        for field, diff in sample_diffs:
            print(f"字段: {field}")
            print(f"旧版本: {diff['system1']}")
            print(f"新版本: {diff['system2']}")
            print("-" * 40)

        # 根据差异类型给出总体建议
        if "字段缺失" in summary:
            print("\n建议: 检查API字段兼容性，确保两个版本返回的字段一致")
        if "复杂类型差异" in summary:
            print("建议: 重点关注复杂类型(对象/数组)的结构差异")
        if "简单类型差异" in summary:
            print("建议: 检查简单类型字段的业务逻辑是否正确")


def main():
    print("开始执行系统差异比较...")
    setup_directories()

    # 启动比较线程
    compare_threads = []
    for _ in range(CONFIG["max_workers"]):
        t = threading.Thread(target=compare_files_worker)
        t.start()
        compare_threads.append(t)

    # 获取数据，会自动将文件对放入队列
    fetch_data_for_dates()

    # 等待所有文件比较完成
    file_pair_queue.join()

    # 停止比较线程
    for t in compare_threads:
        t.join()

    # 生成报告
    generate_reports()
    print("执行完成")


if __name__ == "__main__":
    main()
