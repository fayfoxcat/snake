import json
import os
import zipfile
from elasticsearch import Elasticsearch, helpers
from concurrent.futures import ThreadPoolExecutor

es_config = {
    'url': ['http://172.18.37.193:22030'],
    'basic_auth': ('elastic', 'wiscom123')
}

# 连接到 Elasticsearch
es = Elasticsearch(es_config.get('url'), basic_auth=es_config.get('basic_auth'))

def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def read_zip_file(file_path):
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        for file_name in zip_ref.namelist():
            if file_name.endswith('.json'):
                with zip_ref.open(file_name) as file:
                    return json.load(file)
    return None

# 读取指定目录下的所有JSON文件和ZIP文件中的JSON文件
def read_files_from_directory(directory):
    data = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith('.json'):
                data.append(read_json_file(file_path))
            elif file.endswith('.zip'):
                json_data = read_zip_file(file_path)
                if json_data:
                    data.append(json_data)
    return data

directory_path = 'C:/Users/root/Desktop/ES/single'  # 指定目录路径
data = read_files_from_directory(directory_path)

# 准备要写入 Elasticsearch 的数据
actions = []
for dataset in data:
    for hit in dataset:
        actions.append({
            "_index": hit["_index"],
            "_id": hit["_id"],
            "_source": hit["_source"]
        })

# 每批次处理的数量
batch_size = 10000

def bulk_insert(batch):
    helpers.bulk(es, batch)

# 将数据分批次处理
batches = [actions[i:i + batch_size] for i in range(0, len(actions), batch_size)]

# 使用 ThreadPoolExecutor 进行多线程批量插入
with ThreadPoolExecutor(max_workers=os.cpu_count()*2) as executor:
    executor.map(bulk_insert, batches)

print("数据已成功写入到 Elasticsearch")
