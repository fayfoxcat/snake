import json

# 读取JSON文件
with open('C:/Users/root/Desktop/id.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# 提取_id的值并保留双引号
ids = [f'"{item["_id"]}"' for item in data]

# 逗号分隔输出_id的值
output = ','.join(ids)
print(output)
