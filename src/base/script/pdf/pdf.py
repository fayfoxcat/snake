#!/bin/env python
# -*- coding: UTF-8 -*-
"""
方法用于生成pdf
"""
import copy
import math
from typing import List
from hashlib import sha1
from math import pi, cos, sin
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.colors import HexColor
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus.frames import Frame
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.legends import Legend
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.graphics.widgetbase import TypedPropertyCollection
from reportlab.graphics.shapes import Drawing, String, Line, Circle
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.graphics.charts.barcharts import VerticalBarChart, HorizontalBarChart, BarChartProperties
from reportlab.platypus import TableStyle, Paragraph, PageBreak, PageTemplate, Table, Flowable, Spacer, BaseDocTemplate

# 注册字体
pdfmetrics.registerFont(TTFont('ChineseFont-Slim', 'font/SimSun.ttf'))
pdfmetrics.registerFont(TTFont('ChineseFont-Bold', 'font/微软雅黑粗体.ttf'))

# 页面纸张尺寸、Frame外边距、Frame内边距、Frame尺寸
pageWidth, pageHeight = A4
topMargin, bottomMargin, leftMargin, rightMargin = (50, 50, 50, 50)
leftPadding, bottomPadding, rightPadding, topPadding = (6, 12, 6, 18)
frameWidth, frameHeight = (pageWidth - leftMargin - rightMargin, pageHeight - topMargin - bottomMargin)

# 目录样式
ContentStyle = ParagraphStyle(name='centered', fontName='ChineseFont-Bold', fontSize=17, leftIndent=-leftPadding,
                              leading=18, spaceAfter=10, textColor="#365F91")

# 目录级别样式
ContentsStyle = [
    ParagraphStyle(name='TOCHeading1', fontName='ChineseFont-Slim', fontSize=10, leading=18,
                   leftIndent=-leftPadding),
    ParagraphStyle(name='TOCHeading2', fontName='ChineseFont-Slim', fontSize=10, leading=18,
                   leftIndent=-leftPadding + 10),
    ParagraphStyle(name='TOCHeading3', fontName='ChineseFont-Slim', fontSize=10, leading=18,
                   leftIndent=-leftPadding + 20)
]

# 定义1-4级标题样式
h1 = ParagraphStyle(name='Heading1', fontName='ChineseFont-Bold', fontSize=16, spaceAfter=10, leftIndent=-leftPadding,
                    spaceBefore=10, leading=20)
h2 = ParagraphStyle(name='Heading2', fontName='ChineseFont-Bold', fontSize=14, spaceAfter=10, leftIndent=-leftPadding,
                    spaceBefore=10, leading=20)
h3 = ParagraphStyle(name='Heading3', fontName='ChineseFont-Bold', fontSize=12, spaceAfter=10, leftIndent=-leftPadding,
                    spaceBefore=10, leading=20)
h4 = ParagraphStyle(name='Heading4', fontName='ChineseFont-Slim', fontSize=12, spaceAfter=10, leftIndent=-leftPadding,
                    spaceBefore=10, leading=20)

# 定义全局表格样式
tableStyle = TableStyle([
    ('LINEABOVE', (0, 0), (-1, 0), 1, '#49A8D8'),  # 首行上方线条加粗
    ('LINEABOVE', (0, 0), (-1, -1), 0.5, '#49A8D8'),  # 设置水平上边框
    ('LINEBELOW', (0, -1), (-1, -1), 1, '#49A8D8'),  # 尾行下方线条加粗
    ('LINEBEFORE', (1, 1), (-1, -1), 0.5, '#49A8D8'),  # 设置垂直左边框（不含首行）
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # 文本垂直居中
])

# 表格条件样式：次表头样式、指定列样式、单元格样式
styles = getSampleStyleSheet()
cellStyle = styles['Normal'].clone(name='cellStyle', fontName='ChineseFont-Slim', fontSize=10, alignment=0)

# pdf页面：封面、页眉、目录、正文
Cover = []
PageHeader = None
Contents = [0, 0, 0, 0]
Pages = []


class CustomPageTemplate(BaseDocTemplate):
    """ 定义页面模板样式 """

    def __init__(self, filename, **kw):
        super().__init__(filename, **kw)
        template = PageTemplate('normal', [Frame(leftMargin, bottomMargin, frameWidth, frameHeight,
                                                 topPadding=topPadding, bottomPadding=bottomPadding,
                                                 leftPadding=leftPadding, rightPadding=rightPadding, id='F1')])
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

                # 调整页码，如果有封面则减去封面大小，除2是每个封面都会跟一个换页符
                adjusted_page_num = self.page - len(Cover) / 2

                e = [level, text, adjusted_page_num]
                bn = getattr(flowable, '_bookmarkName', None)
                if bn is not None:
                    e.append(bn)
                self.notify('TOCEntry', tuple(e))


class CoverCanvas(Flowable):
    """ 绘制首页：一个自定义Flowable，用于在文档中绘制Canvas内容 """

    def __init__(self, info):
        Flowable.__init__(self)
        self.img_path = info['coverPath']
        self.type = info.get('reportType', 'a')
        self.info = info
        self.width = frameWidth - (leftPadding + rightPadding)
        self.height = frameHeight - (bottomPadding + topPadding)

    def cover_a(self):
        """ 绘制封面 """
        self.canv.drawImage(self.img_path, -(leftMargin + leftPadding), -(topMargin + topPadding),
                            width=pageWidth, height=pageHeight)

        # 绘制标题
        header = self.info.get("deviceName", None) + " 资源明细报告"
        sub = self.info.get("deviceName", None).replace("_", " ") + " RESOURCE DETAILS"
        self.draw_custom_text(header, 0, 500, "center", "ChineseFont-Bold", 30, "#244B98")
        self.draw_custom_text(sub, 0, 530, "center", "ChineseFont-Bold", 14, "#969897")
        # 计算最长文本起始位置，设置居中
        max_x = max(self.position("资源名称：" + self.info.get("deviceName", None), 0, 0, "center",
                                  "ChineseFont-Bold", 16)[0],
                    self.position("资源名称：" + self.info.get("deviceName", None), 0, 0, "center",
                                  "ChineseFont-Bold", 16)[0],
                    self.position("资源名称：" + self.info.get("deviceName", None), 0, 0, "center",
                                  "ChineseFont-Bold", 16)[0])
        self.draw_custom_text("资源名称：" + self.info.get("deviceName", None), max_x, 600, "left",
                              "ChineseFont-Bold", 16, "#000000")
        self.draw_custom_text("资源类型：" + self.info.get("deviceType", None), max_x, 630, "left",
                              "ChineseFont-Bold", 16, "#000000")
        self.draw_custom_text("资源地址：" + self.info.get("deviceAddress", None), max_x, 660, "left",
                              "ChineseFont-Bold", 16, "#000000")

    def cover_b(self):
        """ 绘制封面 """
        self.canv.drawImage(self.img_path, -(leftMargin + leftPadding), -topMargin - 30,
                            width=pageWidth, height=pageHeight)
        self.draw_custom_text(self.info.get("reportTime", datetime.now().year),
                              60, 520, "left", "ChineseFont-Bold", 40, "#DF8528")
        self.draw_custom_text(self.info.get("reportName", None),
                              60, 570, "left", "ChineseFont-Bold", 40, "#23548A")

    def draw(self):
        if self.type == 'a':
            self.cover_a()
        else:
            self.cover_b()

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

        x, y = self.position(text, x, y, align, font, size)
        # 绘制文本
        self.canv.drawString(x, self.height - y, text)

    def position(self, text, x, y, align, font, size) -> tuple:
        """
        计算文本绘制位置
        :param text: 文本
        :param x: 左下x
        :param y: 左下y
        :param align: 文本
        :param font: 字体
        :param size: 字体大小
        """
        # 计算文本宽度
        text_width = self.canv.stringWidth(text, font, size)

        # 根据对齐方式调整x位置
        if align == "center":
            x += (self.width - text_width) / 2
        elif align == "right":
            x += text_width
        return x, y

    @staticmethod
    def hex_to_rgb(hex_color):
        """
        将16进制颜色转换为RGB格式
        :param hex_color: 16进制色
        :return: RGB色
        """
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


class PageHeaderFooterCanvas(Canvas):
    """ 定义页面页眉页角样式 """

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
        self.header_text = PageHeader

    def showPage(self):
        # 仅当不是封面时，增加页面计数器
        if not self.has_cover:
            self.pages += 1
            self.footer(self.pages)
            if self.header_text is not None:
                self.header(self.header_text)
        else:
            self.has_cover = False  # 第一页之后，取消封面标记
        Canvas.showPage(self)

    def header(self, header_text):
        # 设置页眉的位置和样式
        header_x = leftMargin  # 页眉的横向位置，可以根据需要调整
        header_y = pageHeight - 40  # 页眉的纵向位置，可以根据需要调整
        header_font = "ChineseFont-Bold"  # 页眉的字体，可以根据需要调整
        header_font_size = 10  # 页眉的字号，可以根据需要调整
        header_color = "#2F5496"  # 浅蓝色

        # 设置字体和颜色
        self.setFont(header_font, header_font_size)
        self.setFillColor(header_color)

        # 绘制页眉文本
        self.drawString(header_x, header_y, header_text)

        # 绘制同色横线
        line_width = frameWidth  # 横线的长度，可以根据需要调整
        line_height = header_y - 8  # 横线的位置，略低于文字
        self.setLineWidth(1)  # 横线的宽度，可以根据需要调整
        self.setStrokeColor("#3480B7")
        self.line(header_x, line_height, header_x + line_width, line_height)

    def footer(self, page_number):
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


class CustomTable:
    def __init__(self, data, pattern=None, merge_columns=None):
        self.data = data
        self.pattern = pattern
        self.merge_columns = merge_columns
        self.valid_styles = ['ALIGN', 'VALIGN', 'FONT', 'TEXTCOLOR', 'BACKGROUND', 'GRID', 'BOX', 'SPAN',
                             'FONTSIZE', 'LEFTPADDING', 'RIGHTPADDING', 'TOPPADDING', 'BOTTOMPADDING',
                             'LINEABOVE', 'LINEBELOW', 'LINEBEFORE', 'LINEAFTER', 'COLWIDTHS', 'ROWHEIGHTS',
                             'LEADING', 'INDENT', 'SPACEBEFORE', 'SPACEAFTER', 'BORDERWIDTH', 'BORDERCOLOR']

    def insert_table(self) -> Table:
        """
        插入表格内容
        :return: 表格
        """
        # 表头、列表数据
        columns = max([sum(item.get('size', 1) for item in row) for row in self.data])
        # 处理文本样式
        rows = self.text_style()
        # 创建表格, 固定首行行高，其余行行高自适应
        table = Table(rows, rowHeights=([27] + [None] * (len(rows) - 1)),
                      colWidths=frameWidth / columns)

        # 设置默认样式和自定义样式
        table.setStyle(tableStyle)
        for item in self.pattern:
            style_type = item.get('type')
            # 检查属性是否合法
            if style_type in self.valid_styles:
                table.setStyle(TableStyle([(style_type,
                                            (item.get('start_x', 0), item.get('start_y', 0)),
                                            (item.get('end_x', -1), item.get('end_y', -1)),
                                            item.get("line_width", 0.5), item.get('color', None))]))
            else:
                print(f"警告: 样式 '{style_type}' 不是表格支持的合法样式，仅支持样式：'{self.valid_styles}'")
        # 处理单元格样式
        self.cell_style(table)
        self.merge_cell(table)
        return table

    def text_style(self) -> []:
        """
        自动换行并为指定列应用数据样式
        """
        # 行数,列数（size指定占用多个单元格数量）
        max_row = len(self.data)
        max_column = max([sum(item.get('size', 1) for item in row) for row in self.data])
        result: List[List] = [[None for _ in range(max_column)] for _ in range(max_row)]
        for ri, row in enumerate(self.data):
            offset = 0  # 占用多个单元格偏移量
            for ci, item in enumerate(row):
                style = copy.deepcopy(cellStyle)
                style.textColor = item.get("color", colors.black)
                style.alignment = item.get("alignment", 0)
                style.fontName = "ChineseFont-Bold" if item.get("bold") else "ChineseFont-Slim"
                value = item.get("value")
                if value is not None:
                    result[ri][ci + offset] = Paragraph(str(value), style)
                size = item.get("size", 1)
                offset += size - 1 if size > 1 else 0
        return result

    #
    def cell_style(self, table) -> None:
        """
        定义单元格样式
        :param table: 表格
        """
        for ri, row in enumerate(self.data):
            # 累计单元格偏移量
            offset = 0
            for ci, cell in enumerate(row):
                if cell is not None:
                    table.setStyle(
                        TableStyle(
                            [('BACKGROUND', (ci + offset, ri), (ci + offset, ri), cell.get('background', None))]))
                    # 处理合并单元格
                    size = cell.get('size', 1)
                    if size > 1:
                        table.setStyle(TableStyle([('SPAN', (ci + offset, ri), (ci + offset + size - 1, ri))]))
                        offset += size - 1

    def merge_cell(self, table: Table) -> None:
        """
        指定列若含相同数据，则自动合并单元格
        :param table: 表格
        """
        # 填充空位
        items = copy.deepcopy(self.data)
        for row in items:
            i = 0
            while i < len(row):
                obj = row[i]
                if obj is not None and obj.get('size', 1) > 1:
                    for _ in range(obj['size'] - 1):
                        row.insert(i + 1, None)
                    i += obj['size']
                else:
                    i += 1
        # 准备一个列表来存储所有的合并指令
        merges = []
        # 遍历指定的合并列
        for ci in self.merge_columns:
            row_start = None
            # 遍历每一行
            for ri, row in enumerate(items):
                current = row[ci].get('value') if row[ci] else None
                offset = row[ci].get('size', 1) - 1 if row[ci] else 0
                # 检查当前单元格是否为None
                if current is None or ri == len(items) - 1:
                    should_merge = False
                # 检查当前单元格与下一单元格的数据是否不同
                elif items[ri + 1][ci] is not None and current != items[ri + 1][ci].get('value'):
                    should_merge = False
                else:
                    should_merge = True
                # 判断合并
                if not should_merge:
                    if row_start is not None:
                        merges.append(('SPAN', (ci, row_start), (ci + offset, ri)))
                    row_start = None
                # 记录开始合并起始行
                elif row_start is None:
                    row_start = ri
        # 应用所有的合并指令
        table.setStyle(TableStyle(merges))


class VerticalChart(Flowable):
    def __init__(self, data, label, bars, color_list, legend=None, x=0, y=0, width=400, height=250,
                 value_min=0, value_max=None, value_step=None, font_name="ChineseFont-Slim", font_size=10):
        Flowable.__init__(self)
        self.data = data
        self.label = label
        self.bars = bars
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.fontName = font_name
        self.fontSize = font_size
        self.legend_list = legend
        self.colors = [colors.HexColor(item) for item in color_list]
        self.valueMin = value_min
        self.valueMax = value_max
        self.valueStep = value_step

    def set_legend(self, bar):
        if self.legend_list is None:
            return None
        # 设置图例
        legend = Legend()
        legend.dx = 20  # 图例宽
        legend.dy = 8  # 图例高
        legend.boxAnchor = 'ne'  # 以右上角为锚点定位
        legend.x = bar.x + bar.width  # 将图例放置在图表右上角
        legend.y = bar.y + bar.height + 20
        legend.columnMaximum = 1  # 最大列数，用于控制横向展示
        legend.deltax = 90  # 图例组件之间的水平间距
        legend.alignment = 'right'  # 图例的文本对齐方式
        legend.dxTextSpace = 10  # 图例文本与图例之间的间距
        legend.fontName = self.fontName
        legend.fontSize = self.fontSize - 2
        legend.strokeColor = None  # 图例的边框颜色
        # 图例颜色和文本
        legend.colorNamePairs = [(self.colors[index], item) for index, item in enumerate(self.legend_list)]
        return legend

    def draw(self):
        text_width = self.canv.stringWidth(max(self.data, key=lambda x: len(x[self.label]))[self.label],
                                           self.fontName, self.fontSize)
        d = Drawing(self.width, self.height)
        bar = VerticalBarChart()
        bar.height = self.height * 0.6
        bar.width = self.width * 0.8
        bar.x = (d.width - bar.width) / 2
        bar.y = text_width + 10
        bar.data = [[item[bar] for item in self.data] for bar in self.bars]
        bar.categoryAxis.categoryNames = [item[self.label] for item in self.data]

        # 设置横坐标
        label_width = bar.width / len(self.data)
        bar.categoryAxis.labels.fontName = self.fontName
        bar.categoryAxis.labels.fontSize = self.fontSize
        bar.categoryAxis.strokeWidth = 0.5  # 设置横坐标的粗细
        bar.categoryAxis.labels.dy = 0
        if label_width < text_width:
            radio = label_width / (text_width + 30)
            bar.categoryAxis.labels.angle = math.degrees(math.acos(radio))  # 设置横坐标的文字倾斜角度
            bar.categoryAxis.labels.dx = - self.fontSize / 1.5  # 根据字体大小自适应
            bar.categoryAxis.labels.dy = - math.sqrt((text_width + 20) ** 2 - label_width ** 2) / 2  # 根据文本宽度自动自适应

        # 设置纵坐标
        bar.valueAxis.strokeWidth = 0.5  # 设置纵坐标的粗细
        bar.valueAxis.valueMin = self.valueMin
        bar.valueAxis.valueMax = self.valueMax
        bar.valueAxis.valueStep = self.valueStep
        bar.valueAxis.labels.fontName = self.fontName
        bar.valueAxis.labels.fontSize = 10
        # bar.valueAxis.labelFormat = '%d'  # 可以设置刻度标签的格式

        # 设置网格线
        bar.valueAxis.visibleGrid = True
        bar.valueAxis.gridStrokeColor = colors.lightgrey  # 设置网格线的颜色
        bar.valueAxis.gridStart = bar.x  # 网格线开始的位置
        bar.valueAxis.gridEnd = bar.x + bar.width  # 网格线结束的位置

        # 设置柱子
        bar.barWidth = 7
        style = TypedPropertyCollection(BarChartProperties)  # 设置柱子样式
        style.strokeColor = None  # 去掉柱子的边框
        bar.bars = style
        for index in range(len(bar.data)):
            bar.bars[index].fillColor = self.colors[index]

        d.add(self.set_legend(bar))
        d.add(bar)
        # 绘制到canvas
        d.drawOn(self.canv, (frameWidth - leftPadding - rightPadding - self.width) / 2 + self.x, self.y)


class HorizontalChart(Flowable):
    def __init__(self, data, label, bars, color_list, legend=None, x=0, y=0, width=400, height=200, label_len_max=200,
                 value_min=0, value_max=None, value_step=None, font_name="ChineseFont-Slim", font_size=10):
        Flowable.__init__(self)
        self.data = data
        self.label = label
        self.bars = bars
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.fontName = font_name
        self.fontSize = font_size
        self.legend_list = legend
        self.colors = [HexColor(item) for item in color_list]
        self.valueMin = value_min
        self.valueMax = value_max
        self.valueStep = value_step
        self.label_len_max = label_len_max

    def set_legend(self, bar):
        if self.legend_list is None:
            return None
        legend = Legend()
        legend.dx = 20
        legend.dy = 8
        legend.boxAnchor = 'ne'
        legend.x = bar.x + bar.width
        legend.y = bar.y + bar.height + 20
        legend.columnMaximum = 1
        legend.deltax = 90
        legend.alignment = 'right'
        legend.dxTextSpace = 10
        legend.fontName = self.fontName
        legend.fontSize = self.fontSize - 2
        legend.strokeColor = None
        legend.colorNamePairs = [(self.colors[index], item) for index, item in enumerate(self.legend_list)]
        return legend

    def char_length(self, c):
        # 全角字符 (包括中文字符和全角标点)
        if '\u4e00' <= c <= '\u9fff' or '\uff01' <= c <= '\uff60' or '\u3000' <= c <= '\u303f':
            return 1 * self.fontSize
        # 英文字母（无论大小写）
        elif c.isalpha():
            return 0.6 * self.fontSize
        # 半角 标点、半角 字符、其他数字
        else:
            return 0.5 * self.fontSize

    def wrap_text(self, text):
        wrapped_text = ""
        current_length = 0
        for char in text:
            current_length += self.char_length(char)
            if current_length > self.label_len_max:
                wrapped_text += '\n'
                current_length = self.char_length(char)
            wrapped_text += char

        return wrapped_text

    def draw(self):
        max_label_width = min(self.label_len_max, max(
            [self.canv.stringWidth(item[self.label], self.fontName, self.fontSize) for item in
             self.data]))
        d = Drawing(self.width, self.height)
        bar = HorizontalBarChart()
        bar.height = self.height * 0.8
        bar.width = self.width - max_label_width
        bar.x = max_label_width
        bar.y = (self.height - bar.height) / 2
        bar.data = [[item[bar] for item in self.data] for bar in self.bars]

        # 设置纵坐标
        bar.categoryAxis.categoryNames = [self.wrap_text(item[self.label]) for item in self.data]
        bar.categoryAxis.labels.fontName = self.fontName
        bar.categoryAxis.labels.fontSize = self.fontSize
        bar.categoryAxis.strokeWidth = 0
        bar.categoryAxis.strokeColor = None

        # 设置横坐标
        bar.valueAxis.strokeWidth = 0
        bar.valueAxis.strokeColor = None
        bar.valueAxis.valueMin = self.valueMin
        bar.valueAxis.valueMax = self.valueMax
        bar.valueAxis.valueStep = self.valueStep
        bar.valueAxis.labels.fontName = self.fontName
        bar.valueAxis.labels.fontSize = self.fontSize

        # 设置网格线
        bar.valueAxis.visibleGrid = True
        bar.valueAxis.gridStrokeColor = colors.lightgrey
        bar.valueAxis.gridStart = bar.y
        bar.valueAxis.gridEnd = bar.y + bar.height

        # 设置柱子
        bar.barWidth = 4
        style = TypedPropertyCollection(BarChartProperties)  # 设置柱子样式
        style.strokeColor = None  # 去掉柱子的边框
        bar.bars = style
        for index in range(len(bar.data)):
            bar.bars[index].fillColor = self.colors[index]
        d.add(self.set_legend(bar))
        d.add(bar)
        d.drawOn(self.canv, (frameWidth - leftPadding - rightPadding - self.width) / 2 + self.x, self.y)


class PieChart(Flowable):
    def __init__(self, data, tag=None, x=0, y=0, radius=80, font_name=None, font_size=10, label_distance=None):
        Flowable.__init__(self)
        self.tag = tag
        self.data = data
        self.x = x
        self.y = y
        self.radius = radius
        self.width = radius * 4
        self.height = radius * 3
        self.label_distance = radius / 2 if label_distance is None else label_distance
        self.font_name = font_name
        self.font_size = font_size

    def calculate_label_position(self, line_start_x, line_start_y, angle, text):
        # 使用 label_distance 调整标签坐标
        label_x = line_start_x + self.label_distance * cos(angle * pi / 180)
        label_y = line_start_y + self.label_distance * sin(angle * pi / 180)
        if 90 <= angle % 360 < 270:
            label_x -= (len(text) * 10 * 0.6)
            label_y -= 10
        elif 0 <= angle % 360 < 30 or 330 <= angle % 360 < 360:
            label_x += 10
        return label_x, label_y

    def calculate_label_midpoints(self, label_x, label_y, angle, text):
        # 估计标签尺寸,字体尺寸*0.7估计系数
        label_width = len(text) * self.font_size * 0.7
        label_height = self.font_size

        # 计算中点位置
        if 45 <= angle % 360 < 170:
            return label_x + label_width / 2 - 5, label_y - 5
        elif 170 <= angle % 360 < 190:
            return label_x + label_width - 5, label_y + label_height / 2 - 5
        elif 190 <= angle % 360 < 315:
            return label_x + label_width / 2 + 5, label_y + label_height + 5
        else:
            return label_x - 5, label_y + label_height / 2 - 5

    def generate_label(self, pie, d):
        total = sum(pie.data)
        # 计算并添加标签和线条
        start_angle = 90
        # 绘制标签
        for item in self.data:
            # 标签文本
            label_text = f'{item["name"]} ({item["count"]})'

            # 计算每个扇形的中点角度
            angle = (item["count"] / total) * 360
            mid_angle = start_angle - angle / 2
            start_angle -= angle

            # 计算扇区弧线中点坐标
            radius = pie.width / 2
            mid_arc_x = radius * cos(mid_angle * pi / 180) + pie.x + radius
            mid_arc_y = radius * sin(mid_angle * pi / 180) + pie.y + radius

            # 计算饼图中心点坐标
            center_x = pie.x + radius
            center_y = pie.y + radius

            # 计算线条的新起始坐标（从饼图中心到扇形的边缘中点连线的3/4处）
            line_start_x = center_x + 0.75 * (mid_arc_x - center_x)
            line_start_y = center_y + 0.75 * (mid_arc_y - center_y)

            # 添加标签
            label_x, label_y = self.calculate_label_position(line_start_x, line_start_y, mid_angle, label_text)
            d.add(String(label_x, label_y, label_text, fillColor=colors.black,
                         fontName=self.font_name, fontSize=self.font_size))

            # 绘制线条
            line_end_x, line_end_y = self.calculate_label_midpoints(label_x, label_y, mid_angle, label_text)
            d.add(Line(line_start_x, line_start_y, line_end_x, line_end_y, strokeColor=HexColor("#A6A6A6")))

    def draw(self):
        # 新建画布，指定位置
        draw = Drawing(self.width, self.height)

        # 绘制饼图：大小、位置
        pie = Pie()
        pie.width = pie.height = self.radius * 2
        pie.x = (draw.width - pie.width) / 2
        pie.y = (draw.height - pie.width) / 2

        # 设置饼图各部分的数量
        pie.data = [item["cont"] for item in self.data]
        # 设置饼图各部分的颜色
        for i, item in enumerate(self.data):
            pie.slices[i].fillColor = colors.HexColor(item["color"])

        # 设置标签

        draw.add(pie)
        self.generate_label(pie, draw)
        draw.drawOn(self.canv, (frameWidth - leftPadding - rightPadding - self.width) / 2 + self.x, self.y)


class RingChart(PieChart):

    def circle(self, pie, draw):
        # 绘制覆盖饼图的同心圆
        circle = Circle(cx=self.radius + pie.x, cy=self.radius + pie.y, r=self.radius / 2,
                        fillColor=colors.white, strokeColor=colors.white)
        # 设置标签
        self.generate_label(pie, draw)
        draw.add(circle)
        # 计算总数
        total_count = sum(pie.data)
        # 创建用于显示总数的字符串
        tag_str = String(self.radius + pie.x, self.radius + pie.y + 2 / 3 * self.font_size,
                         self.tag if self.tag else "总数",
                         textAnchor='middle')
        total_str = String(self.radius + pie.x, self.radius + pie.y - 2 / 3 * self.font_size, str(total_count),
                           textAnchor='middle')

        # 设置文本样式（例如字体大小、颜色等）
        tag_str.fontName = total_str.fontName = self.font_name
        tag_str.fontSize = total_str.fontSize = self.font_size
        tag_str.fillColor = total_str.fillColor = colors.black

        draw.add(tag_str)
        draw.add(total_str)

    def draw(self):
        # 新建画布，指定位置
        draw = Drawing(self.width, self.height)

        # 绘制饼图：大小、位置
        pie = Pie()
        pie.width = pie.height = self.radius * 2
        pie.x = (draw.width - pie.width) / 2
        pie.y = (draw.height - pie.width) / 2

        # 设置饼图各部分的数量
        pie.data = [item["count"] for item in self.data]
        # 设置饼图各部分的颜色
        for i, item in enumerate(self.data):
            pie.slices[i].fillColor = colors.HexColor(item["color"])
            pie.slices[i].strokeColor = colors.white
            pie.slices[i].strokeWidth = 2
        draw.add(pie)
        draw.add(self.circle(pie, draw))
        draw.drawOn(self.canv, (frameWidth - leftPadding - rightPadding - self.width) / 2 + self.x, self.y)


def contents(title) -> List[Paragraph]:
    """
    生成目录,关联链接
    :param title: 目录内容
    :return: 样式列表
    """
    content_list = []

    for item in title:
        text = item.get('name')
        if item.get('level') == 1:
            style = h1
            Contents[0] += 1
            Contents[-3:] = [0, 0, 0]
            text = str(Contents[0]) + ". " + text
        elif item.get('level') == 2:
            style = h2
            Contents[1] += 1
            Contents[-2:] = [0, 0]
            text = str(Contents[0]) + "." + str(Contents[1]) + ". " + text
        elif item.get('level') == 3:
            style = h3
            Contents[2] += 1
            Contents[3] = 0
            text = str(Contents[0]) + "." + str(Contents[1]) + "." + str(Contents[2]) + ". " + text
        else:
            style = h4

        style.textColor = item.get("color", colors.black)
        bn = sha1((text + style.name).encode()).hexdigest()
        link = Paragraph(text + '<a name="%s"/>' % bn, style)
        link._bookmarkName = bn
        content_list.append(link)
    return content_list


def build(filename: str, header=None) -> None:
    """
    函数接受数据参数并生成PDF
    :param filename: 指定文件路径文件名
    :param header: 设置页眉
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
    pdf = CustomPageTemplate(filename, pagesize=A4)
    global PageHeader
    PageHeader = header
    pdf.multiBuild(doc, canvasmaker=PageHeaderFooterCanvas)


def addCover(info) -> None:
    """ 添加封面
    :param info: 封面信息
    """
    Cover.append(CoverCanvas(info))
    Cover.append(PageBreak())


def addContent(body: List[dict]) -> None:
    """ 添加文本内容、List[dict]格式指明标题等级1、2、3为标题
    例：body=[{'level': 1, 'content': "一、一级标题"}]
    :param body: 文本内容
    """
    Pages.extend(contents(body))


def addTitle(name=None, tag=None, serial=True, color=colors.red, font_name="ChineseFont-Slim", bold=True,
             font_size=12, alignment=0, font_color=colors.black, leading=20, leftIndent=-leftPadding, space=10) -> None:
    """
    添加四级标题
    :param name: 标题名
    :param tag: 标签
    :param serial: 是否添加标题序号，默认添加
    :param color: 标签字体颜色
    :param font_name: 字体
    :param bold: 是否加粗
    :param font_size: 字体大小
    :param alignment: 文本对齐，0向右，1居中
    :param font_color: 字体颜色
    :param leading: 行间距
    :param leftIndent: 左间距
    :param space: 空格
    :return:
    """
    if bold:
        font_name = "ChineseFont-Bold"
    if name is None:
        return None
    style = ParagraphStyle(
        'ColoredText',
        parent=styles['Normal'],
        fontName=font_name,
        font_color=font_color,
        fontSize=font_size,
        alignment=alignment,
        leftIndent=leftIndent,
        spaceBefore=space,
        spaceAfter=space,
        leading=leading
    )
    if serial:
        Contents[3] += 1
        no = str(Contents[0]) + "." + str(Contents[1]) + "." + str(Contents[2]) + "." + str(Contents[3]) + ". "
        name = no + name

    title = f"{name}"
    if tag:
        title = title + f"<font color={color}>{'&nbsp;' * 5}{tag}</font>"
    paragraph = Paragraph(title, style)
    Pages.append(paragraph)


def addParagraph(content: str, font_size=10.5, font_color=colors.black, leading=15, leftIndent=-leftPadding,
                 space=5) -> None:
    """
     添加一个自动换行的段落
    :param content: 段落内容
    :param font_size: 字体大小
    :param font_color: 字体颜色
    :param leading: 行间距
    :param leftIndent: 左间距
    :param space: 空格
    """
    # 获取默认样式表，如果没有提供特定样式
    style = ParagraphStyle(
        'contentText',
        parent=styles['Normal'],
        fontName='ChineseFont-Slim',
        font_color=font_color,
        fontSize=font_size,
        leading=leading,
        spaceBefore=space,
        spaceAfter=space,
        leftIndent=leftIndent,
        firstLineIndent=font_size * 2  # 设置首行缩进
    )

    # 创建段落
    paragraph = Paragraph(content, style)
    Pages.append(paragraph)


def addText(text: List[dict]) -> None:
    """
    添加文本
    :param text: 文本内容
    """
    for item in text:
        addTitle(item.get("title"), serial=False, font_name="ChineseFont-Bold", space=3, leftIndent=-leftPadding + 10)
        if item.get("content"):
            addParagraph(item.get("content"), leftIndent=-leftPadding + 10, space=3)


def addTable(table: List[List[dict[str, str]]], columns: List, pattern=None, annotation=None) -> None:
    """ 添加表格
    :param table: 表格数据
    :param columns: 指定列相同数据自动合并单元格
    :param pattern: 自定义样式
    :param annotation: 表注
    """
    pattern = [] if pattern is None else pattern
    Pages.append(Spacer(1, 12))
    Pages.append(CustomTable.insert_table(CustomTable(table, pattern=pattern, merge_columns=columns)))
    if annotation:
        addTitle(annotation.get("content"), serial=False, font_size=10, alignment=annotation.get("alignment", 0))
    Pages.append(Spacer(1, 12))


def addVerticalChart(data: List[dict[str, str]], bars: List[str],
                     label='name', legend=None, color_list=None, annotation=None) -> None:
    """
    添加垂直柱状图
    :param data: 图表数据
    :param bars: 柱状图显示数据列表
    :param label: 横坐标标签
    :param legend: 图例说明列表
    :param color_list: 柱状图显示数据列颜色列表
    :param annotation: 图注
    """
    if color_list is None:
        color_list = ["#4472C4", "#ED7D31", "#FFC000"]
    Pages.append(VerticalChart(data=data, label=label, bars=bars, color_list=color_list, legend=legend))
    if annotation:
        addTitle(annotation.get("content"), serial=False, font_size=10, leftIndent=0,
                 alignment=annotation.get("alignment", 0))


def addHorizontalChart(data: List[dict[str, str]], bars: List[str],
                       label='name', legend=None, color_list=None, annotation=None):
    """
    添加水平柱状图
    :param data: 图表数据
    :param bars: 柱状图显示数据列表
    :param label: 横坐标标签
    :param legend: 图例说明列表
    :param color_list: 柱状图显示数据列颜色列表
    :param annotation: 图注
    :return:
    """
    if color_list is None:
        color_list = ["#FFC000", "#4472C4", "#ED7D31"]
    Pages.append(
        HorizontalChart(data, label, bars, color_list, legend, font_size=7, label_len_max=200, width=400, height=200))
    if annotation:
        addTitle(annotation.get("content"), serial=False, font_size=10, leftIndent=0,
                 alignment=annotation.get("alignment", 0))


def addPie(data, annotation=None):
    """
    添加饼图
    :param data: 数据
    :param annotation: 图注
    """
    Pages.append(PieChart(font_name="ChineseFont-Slim", data=data, label_distance=20, radius=50, font_size=8))
    if annotation:
        addTitle(annotation.get("content"), serial=False, font_size=10, leftIndent=0,
                 alignment=annotation.get("alignment", 0))


def addRing(data: List[dict[str, str]], tag=None, annotation=None):
    """
    添加环图
    :param data: 数据
    :param tag: 环中心显示
    :param annotation: 图注
    """
    Pages.append(
        RingChart(font_name="ChineseFont-Slim", data=data, radius=80, font_size=10, tag=tag))
    if annotation:
        addTitle(annotation.get("content"), serial=False, font_size=10, leftIndent=0,
                 alignment=annotation.get("alignment", 0))
