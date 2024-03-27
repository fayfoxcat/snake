import json

from pdf import addCover, addContent, addTable, build, addVerticalChart, addPie, addRing, \
    addHorizontalChart, addTitle, addText

with open('resources/data1.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
    reportName = data.get('reportName', '汇总报告.pdf')
    cover = data.get('cover')
    addCover(cover)
    for part in data.get('parts', []):
        addContent(part.get("headline", []))
        for group in part.get('groups', []):
            title = group.get('fourth', None)
            if title:
                addTitle(name=title.get('name', None), tag=title.get('tag', None), color=title.get('color', None),
                         bold=title.get('bold', False))
            addText(group.get('text', []))
            for item in group.get('table', []):
                addTable(item.get('data', None), columns=item.get('columns', []), pattern=item.get("pattern", None),
                         annotation=item.get("annotation", None))
            for chart in group.get('verticalCharts', []):
                addVerticalChart(chart.get('data', []), bars=chart.get('bars', None), legend=chart.get('legend', []),
                                 annotation=chart.get("annotation", None))
            for chart in group.get('horizontalCharts', []):
                addHorizontalChart(chart.get('data', []), bars=chart.get('bars', []), legend=chart.get('legend', []),
                                   annotation=chart.get("annotation", None))
            for chart in group.get('pieCharts', []):
                addPie(chart.get('data', []), annotation=chart.get("annotation", None))
            for chart in group.get('ringCharts', []):
                addRing(chart.get('data', []), chart.get('tag', None), annotation=chart.get("annotation", None))
    # 调用函数生成PDF
    build(reportName, header=data.get('pageHeader', None))
