import json

import pandas as pd
from reportlab.lib import pagesizes
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph

# 注册字体
pdfmetrics.registerFont(TTFont('ChineseFont', 'font/SimSun.ttf'))
pdfmetrics.registerFont(TTFont('ChineseFont-Bold', 'font/微软雅黑粗体.ttf'))

# 定义全局表格样式
global_table_style = TableStyle([
    ('SPAN', (0, 0), (-1, 0)),  # 首行合并单元格
    ('BACKGROUND', (0, 0), (-1, 0), "#A1C4E7"),  # 设置第二行的背景色为浅蓝色
    ('GRID', (0, 1), (-1, -1), 1, '#49A8D8'),  # 定义网格线，从第二行开始
    ('BOX', (0, 0), (-1, -1), 1, '#49A8D8'),  # 整体边框
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # 文本垂直居中
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # 第一列向左对齐
    ('FONTNAME', (0, 1), (-1, 1), 'ChineseFont-Bold'),  # 第二行字体加粗
    ('FONTNAME', (0, 0), (-1, 0), 'ChineseFont'),  # 其他行使用注册的中文字体
    ('FONTNAME', (0, 2), (-1, -1), 'ChineseFont'),  # 其他行使用注册的中文字体
    ('FONTSIZE', (0, 0), (-1, -1), 10),  # 字体大小
    ('LINEABOVE', (0, 0), (-1, 0), 1.5, '#49A8D8'),  # 首行上方线条加粗
    ('LINEBELOW', (0, -1), (-1, -1), 1.5, '#49A8D8'),  # 尾行下方线条加粗
    ('LINEBEFORE', (0, 0), (0, -1), 0, '#FFFFFF'),  # 设置第一列左边框为白色
    ('LINEAFTER', (-1, 0), (-1, -1), 0, '#FFFFFF'),  # 设置最后一列右边框为白色
])


# 设置页码
class number_page_canvas(Canvas):
    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)
        self.pages = 0  # 初始化页面计数器

    def showPage(self):
        self.pages += 1  # 页面计数器加一
        self.draw_page_number(self.pages)  # 为当前页面添加页码
        Canvas.showPage(self)

    def draw_page_number(self, page):
        # 绘制阴影矩形
        self.setFillColor("#808080")
        self.rect(180 * mm, 10 * mm, 12 * mm, 6 * mm, fill=True, stroke=False)
        # 绘制间隙矩形
        self.setFillColor("#FFFFFF")
        self.rect(180 * mm, 10.5 * mm, 12 * mm, 6 * mm, fill=True, stroke=False)
        # 绘制主矩形
        self.setFillColor("#2AB4E9")
        self.rect(180 * mm, 11.5 * mm, 12 * mm, 6 * mm, fill=True, stroke=False)
        # 设置页码文字样式
        self.setFillColor("#FFFFFF")
        self.setFont("Helvetica-Bold", 14)
        self.drawString(184 * mm, 13 * mm, str(page))


# 函数接受数据参数并生成PDF
def create_pdf(filename, title, header, data, style=None):
    pdf = SimpleDocTemplate(filename, pagesize=pagesizes.A4)
    elements = [create_title(item) for item in title] + [set_table(header, data, style)]
    pdf.build(elements, canvasmaker=number_page_canvas)


def create_title(title):
    level = title.get('level')
    content = title.get('content')
    # 设置样式
    font_name = 'ChineseFont-Bold' if level in (1, 2, 3) else 'ChineseFont'
    font_size = 16 if level == 1 else 14 if level == 2 else 12 if level == 3 else 12
    left_indent = -20
    leading = 15
    alignment = 0
    space_after = 15
    space_before = 15
    custom_style = ParagraphStyle(
        'CustomStyle',
        fontName=font_name,
        fontSize=font_size,
        leftIndent=left_indent,
        leading=leading,
        textColor='black',
        alignment=alignment,
        spaceAfter=space_after,
        spaceBefore=space_before
    )
    return Paragraph(content, custom_style)


# 插入表格内容
def set_table(header, data, style=None):
    if style is None:
        style = []
    # 次行表头、表头
    sub_row = list(data[0].keys())
    header_row = [header] + [""] * (len(sub_row) - 1)
    # 表格宽度
    table_width = 170 * mm
    column_num = len(sub_row)

    # 读取json数据转换为列表
    items = pd.DataFrame(data).values.tolist()

    # 创建表格
    table = Table([header_row] + [sub_row] + items, colWidths=table_width / column_num)
    # 设置全局表格样式
    table.setStyle(global_table_style)

    for item in style:
        set_local_style(table, item, sub_row, items)
    return table


# 定义局部表格样式
def set_local_style(table, element, sub_row, items):
    for i, item in enumerate(items):
        for j, cell in enumerate(item):
            if sub_row[j] == element.get('column') and element.get('expression')(cell):
                table.setStyle(TableStyle([('BACKGROUND', (j, i + 2), (j, i + 2), element.get('color'))]))


# 表格的表头
title = [{'level': 1, 'content': "2 网络设备"},
         {'level': 2, 'content': "2.1 网络状态检查"},
         {'level': 3, 'content': "2.1.1 VRRP 运行状态"},
         {'level': 4, 'content': "2.1.1.1 VRRP 运行状态"}]
header = "Device_Information"
custom_style = [{'column': 'Type', 'expression': lambda x: x is None, 'color': "#FFA500"},
                {'column': 'Online Status', 'expression': lambda x: x < 60, 'color': "#FA5050"}]

# 示例多行数据
with open('resources/data.json', 'r') as file:
    # 使用json.load()方法加载JSON数据
    example_data = json.load(file)
    # 调用函数生成PDF
    create_pdf("out/网络设备.pdf", title, header, example_data, custom_style)
