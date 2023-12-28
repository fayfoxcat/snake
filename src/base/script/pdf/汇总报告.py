#!/bin/env python
# -*- coding: UTF-8 -*-
"""
方法用于生成pdf，依次需求调用cover反复调用 addText addTable构建pdf页面，调用build生成pdf文档
"""
import logging
from hashlib import sha1
from typing import List

import pandas as pd
from reportlab.lib import pagesizes
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import TableStyle, Paragraph, PageBreak, PageTemplate, Table, SimpleDocTemplate, Flowable
from reportlab.platypus.frames import Frame
from reportlab.platypus.tableofcontents import TableOfContents

# 注册字体
pdfmetrics.registerFont(TTFont('ChineseFont-Slim', 'font/SimSun.ttf'))
pdfmetrics.registerFont(TTFont('ChineseFont-Bold', 'font/微软雅黑粗体.ttf'))

# 目录样式
ContentStyle = ParagraphStyle(name='centered', fontName='ChineseFont-Bold', fontSize=17, leftIndent=-10, leading=12,
                              spaceAfter=10, textColor="#365F91")
ContentsStyle = [
    ParagraphStyle(name='TOCHeading1', fontName='ChineseFont-Slim', fontSize=10, leading=12, leftIndent=-10),
    ParagraphStyle(name='TOCHeading2', fontName='ChineseFont-Slim', fontSize=10, leading=12, leftIndent=0),
    ParagraphStyle(name='TOCHeading3', fontName='ChineseFont-Slim', fontSize=10, leading=12, leftIndent=10)
]

# 定义1-4级标题样式
h1 = ParagraphStyle(name='Heading1', fontName='ChineseFont-Bold', fontSize=16, leftIndent=-20, spaceBefore=10,
                    leading=20)
h2 = ParagraphStyle(name='Heading2', fontName='ChineseFont-Bold', fontSize=14, leftIndent=-20, spaceBefore=10,
                    leading=20)
h3 = ParagraphStyle(name='Heading3', fontName='ChineseFont-Bold', fontSize=12, leftIndent=-20, spaceBefore=10,
                    leading=20)
h4 = ParagraphStyle(name='Heading4', fontName='ChineseFont-Slim', fontSize=12, leftIndent=-20, spaceBefore=10,
                    leading=20)

# 定义全局表格样式
tableStyle = TableStyle([
    ('SPAN', (0, 0), (-1, 0)),  # 首行合并单元格
    ('BACKGROUND', (0, 0), (-1, 0), "#A1C4E7"),  # 设置第一行的背景色为浅蓝色
    ('GRID', (0, 1), (-1, -1), 1, '#49A8D8'),  # 定义网格线，从第二行开始
    ('BOX', (0, 0), (-1, -1), 1, '#49A8D8'),  # 整体边框
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # 文本垂直居中
    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # 首行居中对齐
    ('ALIGN', (0, 1), (-1, -1), 'LEFT'),  # 除首行外，其余行向左对齐
    ('FONTNAME', (0, 0), (-1, 0), 'ChineseFont-Bold'),  # 首行字体加粗
    ('FONTSIZE', (0, 0), (-1, -1), 10),  # 字体大小
    ('LINEABOVE', (0, 0), (-1, 0), 1.5, '#49A8D8'),  # 首行上方线条加粗
    ('LINEBELOW', (0, -1), (-1, -1), 1.5, '#49A8D8'),  # 尾行下方线条加粗
    ('LINEBEFORE', (0, 0), (0, -1), 0, '#FFFFFF'),  # 设置第一列左边框为白色
    ('LINEAFTER', (-1, 0), (-1, -1), 0, '#FFFFFF'),  # 设置最后一列右边框为白色
])

# 表格条件样式：次表头样式、指定列样式、单元格样式
styles = getSampleStyleSheet()
subRowStyle = styles['Normal'].clone(name='subRowStyle', fontName='ChineseFont-Bold', fontSize=10)
columnStyles = styles['Normal'].clone(name='subRowStyle', fontName='ChineseFont-Bold', fontSize=10)
cellStyle = styles['Normal'].clone(name='cellStyle', fontName='ChineseFont-Slim', fontSize=10)

# pdf页面：封面、正文
Cover = []
Pages = []


class CanvasDrawing(Flowable):
    """ 绘制首页：一个自定义Flowable，用于在文档中绘制Canvas内容 """

    def __init__(self, img_path, info):
        Flowable.__init__(self)
        self.img_path = img_path
        self.info = info
        self.width = A4[0] - 11
        self.height = A4[1] - 12

    def draw(self):
        # 绘制图片
        self.canv.drawImage(self.img_path, -6, 14, width=A4[0], height=A4[1])

        # 绘制标题
        header = next(iter(self.info.values()), None) + " 资源明细报告"
        sub = next(iter(self.info.values()), None).replace("_", " ") + " RESOURCE DETAILS"
        self.draw_custom_text(header, 0, 570, "center", "ChineseFont-Bold", 30, "#244B98")
        self.draw_custom_text(sub, 0, 600, "center", "ChineseFont-Bold", 14, "#969897")
        for i, item in enumerate(self.info):
            self.draw_custom_text(item + "：" + self.info.get(item), 170, (650 + i * 30), "left",
                                  "ChineseFont-Bold", 16, "#000000")

    def draw_custom_text(self, text, x, y, align, font, size, color):
        """
        绘制自定义文本
        :param text: 文本
        :param x: 左下x
        :param y: 左下y
        :param align: 文本
        :param font: 字体
        :param size: 字体大小
        :param color: 字体颜色
        """
        # 设置字体和大小
        self.canv.setFont(font, size)

        # 转换16进制颜色为RGB
        rgb_color = self.hex_to_rgb(color)
        self.canv.setFillColorRGB(*rgb_color)

        # 计算文本宽度
        text_width = self.canv.stringWidth(text, font, size)

        # 根据对齐方式调整x位置
        if align == "center":
            x += (self.width - text_width) / 2
        elif align == "right":
            x += text_width
        # 绘制文本
        self.canv.drawString(x, self.height - y, text)

    @staticmethod
    def hex_to_rgb(hex_color):
        """
        将16进制颜色转换为RGB格式
        :param hex_color: 16进制色
        :return: RGB色
        """
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


class CustomTemplate(SimpleDocTemplate):
    """ 定义页面模板样式 """

    def __init__(self, filename, **kw):
        super().__init__(filename, **kw)
        template = PageTemplate('normal', [Frame(0, 0, A4[0], A4[1], id='F1')])
        self.addPageTemplates(template)

    def afterFlowable(self, flowable):
        if flowable.__class__.__name__ == 'Paragraph':
            text = flowable.getPlainText()
            style = flowable.style.name
            if style in ['Heading1', 'Heading2', 'Heading3']:
                level = None
                if style == 'Heading1':
                    level = 0
                elif style == 'Heading2':
                    level = 1
                elif style == 'Heading3':
                    level = 2

                # 调整页码，如果有封面则减1
                adjusted_page_num = self.page - 1 if Cover else self.page

                e = [level, text, adjusted_page_num]
                bn = getattr(flowable, '_bookmarkName', None)
                if bn is not None: e.append(bn)
                self.notify('TOCEntry', tuple(e))


class NumberPageCanvas(Canvas):
    """ 定义页面页码样式 """

    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)
        self.pages = 0  # 初始化页面计数器
        self.has_cover = Cover  # 假设第一页是封面
        self.x = 510
        self.y = 30
        self.width = 35
        self.height = 17
        self.fontName = "ChineseFont-Bold"
        self.fontSize = 14

    def showPage(self):
        # 仅当不是封面时，增加页面计数器
        if not self.has_cover:
            self.pages += 1
            self.draw_page_number(self.pages)
        else:
            self.has_cover = False  # 第一页之后，取消封面标记
        Canvas.showPage(self)

    def draw_page_number(self, page_number):
        # 绘制阴影矩形
        self.setFillColor("#808080")
        self.rect(self.x, self.y, self.width, self.height, fill=True, stroke=False)
        # 绘制间隙矩形
        self.setFillColor("#FFFFFF")
        self.rect(self.x, self.y + 2, self.width, self.height, fill=True, stroke=False)
        # 绘制主矩形
        self.setFillColor("#2AB4E9")
        self.rect(self.x, self.y + 4, self.width, self.height, fill=True, stroke=False)
        # 设置页码文字样式（占两位字符）
        self.setFillColor("#FFFFFF")
        self.setFont(self.fontName, self.fontSize)
        # 计算文本宽度
        text_width = self.stringWidth(str(page_number), self.fontName, self.fontSize)
        self.drawString(self.x + (self.width - text_width) / 2, self.y + 7.5, str(page_number))


# 函数接受数据参数并生成PDF
def build(filename: str) -> None:
    """
    生成pdf
    :param filename: 指定文件路径文件名
    """
    doc = []
    toc = TableOfContents()
    toc.levelStyles = ContentsStyle
    toc.dotsMinLevel = 0
    doc.extend(Cover)
    doc.append(Paragraph('目录', ContentStyle))
    doc.append(toc)
    doc.append(PageBreak())
    doc.extend(Pages)
    pdf = CustomTemplate(filename, pagesize=pagesizes.A4)
    pdf.multiBuild(doc, canvasmaker=NumberPageCanvas)


def addCover(coverPath: str, info: tuple) -> None:
    """ 添加封面
    :param coverPath: 封面路径
    :param info: 封面信息
    """
    Cover.append(CanvasDrawing(coverPath, info))
    Cover.append(PageBreak())


# 设置页面内容
def addText(body: List[dict[str, str]]) -> None:
    """ 添加文本内容、List[dict]格式指明标题等级1、2、3为标题、4：为正文
    例：body=[{'level': 1, 'content': "一、一级标题"}]
    :param body: 文本内容
    """
    Pages.extend(contents(body))


def addTable(header: str, table: List[dict], addSubRow: bool = False, columnBold: List[str] = None,
             conditions: List[dict] = None, merge: List[str] = None) -> None:
    """ 添加表格
    :param header: 表格表头
    :param table: 表格数据
    :param addSubRow: 是否自动添加次表头
    :param columnBold: 指定列加粗
    :param conditions: 指定列数据条件判断
    :param merge: 指定列合并单元格
    """
    Pages.append(insert_table(header, table, add_sub_row=addSubRow,
                              column_bold=columnBold, conditions=conditions, merge=merge))


def contents(title) -> List[Paragraph]:
    """
    生成目录
    :param title: 目录内容
    :return: 样式列表
    """
    return [
        heading(item.get('content'),
                h1 if item.get('level') == 1 else h2 if item.get('level') == 2 else h3 if item.get(
                    'level') == 3 else h4)
        for item in title
    ]


#
def heading(text, style) -> Paragraph:
    """
    生成目录和标题关联链接
    :param text: 标题内容
    :param style: 样式
    :return: 样式
    """
    bn = sha1((text + style.name).encode()).hexdigest()
    h = Paragraph(text + '<a name="%s"/>' % bn, style)
    h._bookmarkName = bn
    return h


def insert_table(header, data, add_sub_row=False, column_bold: List[str] = None, conditions=None, merge=None) -> Table:
    """
    插入表格内容
    :param header: 表格表头
    :param data: 表格数据
    :param add_sub_row: 是否自动添加次表头
    :param column_bold: 指定列加粗
    :param conditions: 指定列数据条件判断
    :param merge: 指定列合并单元格
    :return: 表格
    """
    rows = []
    # 次行表头、表头、列表数据
    sub_row = list(data[0].keys())
    header_row = [header] + [""] * (len(sub_row) - 1)
    items = pd.DataFrame(data).values.tolist()
    # 保存一份原始数据，用于cellStyle、mergeCells
    original_sub = [row for row in sub_row]
    original_items = [list(row) for row in items]

    # 组装次行表头、列表数据
    if add_sub_row:
        rows.append(sub_row)
    rows.extend(items)

    # 定义次表头样式，指定列加粗
    columns = None
    if column_bold is not None:
        columns = [original_sub.index(i) for i in column_bold if i in original_sub]
    # 处理数据自动换行
    auto_wrap(rows, is_sub_bold=add_sub_row, column_bold=columns)

    # 创建表格, 固定首行行高，其余行行高自适应
    table = Table([header_row] + rows, rowHeights=([27] + [None] * (len(rows))), colWidths=480 / len(sub_row))
    # 设置全局表格样式
    table.setStyle(tableStyle)
    cell_style(table, conditions, original_sub, original_items, has_sub_header=add_sub_row)
    merge_cells(table, merge, original_sub, original_items)
    return table


def auto_wrap(rows, is_sub_bold=False, column_bold=None) -> None:
    """
    自动换行并为指定列应用固定样式，首行有固定样式。
    :param rows: 表格的行数据，每行是一个列表
    :param is_sub_bold: 次行表头是否加粗
    :param column_bold: 指定列加粗
    """
    for row_index, row in enumerate(rows):
        for column_index, item in enumerate(row):
            # 为首行和指定列应用特定样式
            if is_sub_bold and row_index == 0:
                style = subRowStyle
            elif column_bold and column_index in column_bold:
                style = columnStyles
            else:
                style = cellStyle
            if item is not None:
                row[column_index] = Paragraph(str(item), style)


#
def cell_style(table, conditions, sub_row, items, has_sub_header=True) -> None:
    """
    定义单元格样式
    :param table: 表格
    :param conditions: 条件列表
    :param sub_row: 次级表头
    :param items: 数据
    :param has_sub_header: 是否包含表头
    """
    if conditions is None:
        return
    offset = 2 if has_sub_header else 1
    for element in conditions:
        error_column: bool = True
        for i, item in enumerate(items):
            for j, cell in enumerate(item):
                if error_column and sub_row[j] == element.get('column'):
                    try:
                        if element.get('expression')(cell):
                            table.setStyle(
                                TableStyle([('BACKGROUND', (j, i + offset), (j, i + offset), element.get('color'))]))
                    except Exception as e:
                        # 设置判断列表达式False，跳出该表达式的所有循环
                        error_column = False
                        logging.error(f"conditions中的表达式有误: {e}")


def merge_cells(table, merge, sub_row, items) -> None:
    """
    处理合并单元格
    :param table: 表格
    :param merge: 指定列合并单元格
    :param sub_row: 次行表头
    :param items: 数据
    """
    if merge is None:
        return
    for merge_column in merge:
        if merge_column in sub_row:
            column_index = sub_row.index(merge_column)
            start_row = None
            prev_value = 'unique_nonexistent_value'  # 初始值设为一个唯一的值
            for row_index, row_data in enumerate(items):
                current_value = row_data[column_index]
                # 如果当前值是 None，将其视为一个特殊标记
                if current_value is None:
                    current_value = 'special_null_value'
                if current_value != prev_value:
                    if start_row is not None and row_index - start_row > 1:
                        table.setStyle(
                            TableStyle([('SPAN', (column_index, start_row + 2), (column_index, row_index + 1))]))
                    start_row = row_index
                prev_value = current_value
            # 检查并处理最后一个合并区域
            if start_row is not None and len(items) - start_row > 1:
                table.setStyle(TableStyle([('SPAN', (column_index, start_row + 2), (column_index, len(items) + 1))]))
