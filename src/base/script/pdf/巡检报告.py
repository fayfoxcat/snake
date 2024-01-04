import json

from src.base.script.pdf.pdf import addCover, addContent, addTable, build, addTitle, addText

with open('resources/巡检报告.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
    reportName = data.get('reportName', '巡检报告.pdf')
    cover = data.get('cover')
    addCover(cover)
    for part in data.get('parts', []):
        addContent(part.get("headline", []))
        for group in part.get('groups', []):
            title = group.get('fourth', None)
            if title:
                addTitle(name=title.get('name', None), tag=title.get('tag', None), color=title.get('color', None))
            addText(group.get('text', []))
            for item in group.get('table', []):
                addTable(item.get('data', None), item.get('columns', []), item.get("pattern", None))
    # 调用函数生成PDF
    build(reportName, header=data.get('pageHeader', None))
