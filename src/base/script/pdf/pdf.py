# 表格的表头
import json

from src.base.script.pdf.巡检报告 import build, page

# 示例多行数据
with open('resources/单板运行状态.json', 'r') as file:
    table = json.load(file)
    body = [{'level': 1, 'content': "2 网络设备"},
            {'level': 2, 'content': "2.1 网络状态检查"},
            {'level': 3, 'content': "2.1.1 VRRP 运行状态"},
            {'level': 4, 'content': "2.1.1.1 VRRP 运行状态"}]
    header = "单板运行状态"
    conditions = [{'column': 'Type', 'expression': lambda x: x is None, 'color': "#FFA500"},
                  {'column': 'Online Status', 'expression': lambda x: x < 60, 'color': "#FA5050"}]
    page(body, header, table, conditions=conditions)

with open('resources/OSPF邻居状态.json', 'r') as file:
    table = json.load(file)
    body = [{'level': 3, 'content': "2.3.3  板卡状态"},
            {'level': 4, 'content': "2.3.3.1  单板运行状态"}]
    header = "OSPF邻居状态"
    page(body, header, table, merge=["Process_ID"])

with open('resources/OSPF错误统计.json', 'r') as file:
    table = json.load(file)
    body = [{'level': 4, 'content': "💠 检查结论"}]
    header = "OSPF错误统计"
    page(body, header, table, merge=["Process_ID"])

# 调用函数生成PDF
build("out/巡检报告.pdf")
