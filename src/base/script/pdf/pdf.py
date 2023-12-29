import json

from src.base.script.pdf.巡检报告 import addCover, addContent, addTable, build, addVerticalChart, addPie, addRing, \
    addHorizontalChart, addTitle, addText

with open('resources/设备信息.json', 'r', encoding='utf-8') as file:
    deviceInfo = json.load(file)
    # addCover("resources/cover_a.jpg", deviceInfo)
    addCover("resources/cover_b.jpg", ("2023", "巡检总结报告"), "b")

with open('resources/单板运行状态.json', 'r', encoding='utf-8') as file:
    table = json.load(file)
    body = [{'level': 1, 'content': "2 网络设备"},
            {'level': 2, 'content': "2.1 网络状态检查"},
            {'level': 3, 'content': "2.1.1 VRRP 运行状态"}]
    header = "单板运行状态"
    conditions = [{'column': 'Type', 'expression': lambda x: x is None, 'color': "#FFA500"},
                  {'column': 'Online Status', 'expression': lambda x: x < 60, 'color': "#FA5050"}]
    addContent(body)
    addTitle(name="2.1.1 VRRP 运行状态", tag="告警", color="red")
    addText([
        {
            "title": "检查要求",
            "content": "要求可插拔模块的温度不超过正常范围。若温度值不在回显中提取到的最高最低温度阈值范围内则告警（仅关注物理状态为up且未手工关闭的端口）。"
        },
        {
            "title": "处理建议",
            "content": "请检查设备的可插拔模块是否发生硬件故障或是散热条件较差导致可插拔模块温度异常。"
        },
        {
            "title": "描述",
            "content": "请检查设备的可插拔模块是否发生硬件故障或是散热条件较差导致可插拔模块温度异常。"
        }
    ])
    addTable(header, table, addSubRow=True, conditions=conditions)

with open('resources/OSPF邻居状态.json', 'r', encoding='utf-8') as file:
    table = json.load(file)
    body = [{'level': 3, 'content': "2.3.3  板卡状态"},
            {'level': 4, 'content': "2.3.3.1  单板运行状态"}]
    header = "OSPF邻居状态"
    addContent(body)
    addTable(header, table, addSubRow=True, merge=["Process_ID", "Route_ID", "Address"])

with open('resources/OSPF错误统计.json', 'r', encoding='utf-8') as file:
    table = json.load(file)
    body = [{'level': 4, 'content': " 检查结论"}]
    conditions = [{'column': 'result', 'expression': lambda x: x == "不合格", 'color': "#FA5050"}]
    header = "OSPF错误统计"
    addContent(body)
    addTable(header, table, columnBold=["item"], conditions=conditions)

with open('resources/告警分类统计.json', 'r', encoding='utf-8') as file:
    alarm = json.load(file)
    label = "name"
    bars = ["resources", "alarm", "click"]
    colors = ["#4472C4", "#ED7D31", "#FFC000"]
    legend = ["涉及资源", "告警数量", "确认数量"]
    addVerticalChart(alarm, label, bars, colors, legend)

with open('resources/告警检查项top10汇总.json', 'r', encoding='utf-8') as file:
    alarm = json.load(file)
    label = "name"
    bars = ["count", ]
    colors = ["#FFC000", "#4472C4", "#ED7D31"]
    legend = ["涉及资源", "告警数量", "确认数量"]
    addHorizontalChart(alarm, label, bars, colors, [])

with open('resources/告警级别统计.json', 'r', encoding='utf-8') as file:
    count = json.load(file)
    addPie(count)

with open('resources/告警级别统计.json', 'r', encoding='utf-8') as file:
    count = json.load(file)
    addRing(count)

# 调用函数生成PDF
build("out/巡检报告.pdf")
