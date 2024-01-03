import json

from src.base.script.pdf.pdf import addCover, addContent, addTable, build, addVerticalChart, addPie, addRing, \
    addHorizontalChart, addTitle, addText

with open('resources/汇总报告.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
    reportName = data.get('reportName', '汇总报告.pdf')
    cover = data.get('cover')
    addCover(cover)
    for part in data.get('parts', []):
        addContent([{'level': 1, 'content': part['first']},
                    {'level': 2, 'content': part['second']}])
        for group in part.get('groups', []):
            title = group.get('three', None)
            addTitle(title.get('title', None), title.get('tag', None), title.get('color', None))
            addText(group.get('text', []))
            for chart in group.get('verticalCharts', []):
                addVerticalChart(chart.get('data', []), bars=chart.get('bars', []), legend=chart.get('legend', []))
            for chart in group.get('horizontalCharts', []):
                addHorizontalChart(chart.get('data', []), bars=chart.get('bars', []), legend=chart.get('legend', []))
            for chart in group.get('pieCharts', []):
                addPie(chart.get('data', []))
            for chart in group.get('ringCharts', []):
                addRing(chart.get('data', []), chart.get('tag', None))
    # 调用函数生成PDF
    build(reportName, header=data.get('pageHeader', None))