import json
from datetime import datetime

# 定义筛选条件
target_station_name = "国丰丰海风电"
target_file_type = 3
start_time = "2024-04-01T00:00:00.000Z"
end_time = "2024-05-01T00:00:00.000Z"

# 将时间字符串转换为datetime对象
start_time_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
end_time_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))

# 读取JSON文件
with open('C:/Users/root/Desktop/ES/index_filerecord_202404.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# 创建一个列表来存储符合条件的记录
filtered_records = []

# 遍历每个记录并根据条件进行筛选
for record in data['hits']['hits']:
    source = record['_source']
    station_name = source['stationName']
    file_type = source['fileType']
    upload_time = datetime.fromisoformat(source['uploadTime'].replace("Z", "+00:00"))

    if (station_name == target_station_name and
            file_type == target_file_type and
            start_time_dt <= upload_time <= end_time_dt):
        filtered_records.append(record)

# 将筛选后的记录写入result.json文件
with open('result.json', 'w', encoding='utf-8') as file:
    json.dump(filtered_records, file, ensure_ascii=False, indent=4)

print("符合条件的记录已成功筛选并写入result.json文件。")
