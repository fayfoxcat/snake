import json

from src.base.script.pdf.pdf import addCover, addContent, addTable, build, addTitle, addText

with open('resources/巡检报告.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
    reportName = data.get('reportName', '巡检报告.pdf')
    cover = data.get('cover')
    addCover(cover)
    for part in data.get('parts', []):
        addContent([{'level': 1, 'content': part['first']},
                    {'level': 2, 'content': part['second']}])
        for group in part.get('groups', []):
            title = group.get('three', None)
            addTitle(title.get('title', None), title.get('tag', None), title.get('color', None))
            addText(group.get('text', []))
            for item in group.get('table', []):
                addTable(item.get('data', None), item.get('merge', False))
    # 调用函数生成PDF
    build(reportName, header=data.get('pageHeader', None))


# with open('resources/OSPF错误统计.json', 'r', encoding='utf-8') as file:
#     table = json.load(file)
#     body = [{'level': 4, 'content': " 检查结论"}]
#     header = "OSPF错误统计"
#     addContent(body)
#     # addTable(table, header)


