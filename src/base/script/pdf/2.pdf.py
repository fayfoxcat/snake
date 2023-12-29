import json

from src.base.script.pdf.chart import addText, build, addCover, addVerticalChart, addPie, addRing, addHorizontalChart

with open('resources/设备信息.json', 'r', encoding='utf-8') as file:
    deviceInfo = json.load(file)
    addCover("resources/cover_a.jpg", deviceInfo)

body = [{'level': 1, 'content': "2 网络设备"},
        {'level': 2, 'content': "2.1 网络状态检查"},
        {'level': 3, 'content': "2.1.1 VRRP 运行状态"},
        {'level': 4, 'content': "2.1.1 VRRP 运行状态"}]
header = "单板运行状态"
conditions = [{'column': 'Type', 'expression': lambda x: x is None, 'color': "#FFA500"},
              {'column': 'Online Status', 'expression': lambda x: x < 60, 'color': "#FA5050"}]
addText(body)

with open('resources/告警分类统计.json', 'r', encoding='utf-8') as file:
    alarm = json.load(file)
    label = "name"
    bars = ["resources", "alarm", "click"]
    colors = ["#4472C4", "#ED7D31", "#FFC000"]
    legend = ["涉及资源", "告警数量", "确认数量"]
    addVerticalChart(alarm, label, bars, colors, legend)

addText(body)

with open('resources/告警级别统计.json', 'r', encoding='utf-8') as file:
    count = json.load(file)
    addPie(count)

addText(body)

with open('resources/告警级别统计.json', 'r', encoding='utf-8') as file:
    count = json.load(file)
    addRing(count)

addText(body)

with open('resources/告警检查项top10汇总.json', 'r', encoding='utf-8') as file:
    alarm = json.load(file)
    label = "name"
    bars = ["count", ]
    colors = ["#FFC000", "#4472C4", "#ED7D31"]
    legend = ["涉及资源", "告警数量", "确认数量"]
    addHorizontalChart(alarm, label, bars, colors, [])

# 调用函数生成PDF
build("out/chart.pdf")

