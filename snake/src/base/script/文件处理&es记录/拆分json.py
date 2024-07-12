import json
import os

# 读取JSON文件
with open('C:/Users/root/Desktop/ES/index_filerecord_202405.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# 创建一个字典来存储分组后的数据
grouped_data = {}

# 遍历每个记录并根据stationName进行分组
for record in data['hits']['hits']:
    station_name = record['_source']['stationName']
    if station_name not in grouped_data:
        grouped_data[station_name] = []
    grouped_data[station_name].append(record)

# 为每个stationName创建一个文件并写入数据
for station_name, records in grouped_data.items():
    # 创建文件名，去掉stationName中的特殊字符以避免文件名问题
    safe_station_name = ''.join(e for e in station_name if e.isalnum())
    file_name = f"{safe_station_name}.json"

    # 将记录写入文件
    with open('C:/Users/root/Desktop/ES/part' + file_name, 'w', encoding='utf-8') as file:
        json.dump(records, file, ensure_ascii=False, indent=4)

print("数据已成功分组并写入文件。")
