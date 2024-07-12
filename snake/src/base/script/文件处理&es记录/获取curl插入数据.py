import json

# 输入 JSON 文件名
input_file = 'result.json'

# 输出文件名
output_file = 'data.json'

# 读取 JSON 文件
with open(input_file, 'r', encoding='utf-8') as f:
    input_data = json.load(f)

# 打开文件进行写入
with open(output_file, 'w', encoding='utf-8') as f:
    for record in input_data:
        # 写入操作/元数据行
        action_metadata = {
            "index": {
                "_index": record["_index"],
                "_type": record["_type"],
                "_id": record["_id"],
                "routing": record["_routing"]
            }
        }
        f.write(json.dumps(action_metadata) + '\n')

        # 写入数据行
        f.write(json.dumps(record["_source"]) + '\n')

print(f"Data has been written to {output_file}")
