#!/bin/env python
# -*- coding: UTF-8 -*-
"""
方法用于生成pdf，依次需求调用cover反复调用 addText addTable构建pdf页面，调用build生成pdf文档
"""
import copy
import math
from datetime import datetime
from hashlib import sha1
from math import cos, pi, sin
from typing import List

from reportlab.graphics.charts.barcharts import VerticalBarChart, BarChartProperties, HorizontalBarChart
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing, String, Line, Circle
from reportlab.graphics.widgetbase import TypedPropertyCollection
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import TableStyle, Paragraph, PageBreak, PageTemplate, Table, SimpleDocTemplate, Flowable, \
    Spacer
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
h1 = ParagraphStyle(name='Heading1', fontName='ChineseFont-Bold', fontSize=16, leftIndent=-20, spaceAfter=10,
                    spaceBefore=10, leading=20)
h2 = ParagraphStyle(name='Heading2', fontName='ChineseFont-Bold', fontSize=14, leftIndent=-20, spaceAfter=10,
                    spaceBefore=10, leading=20)
h3 = ParagraphStyle(name='Heading3', fontName='ChineseFont-Bold', fontSize=12, leftIndent=-20, spaceAfter=10,
                    spaceBefore=10, leading=20)
h4 = ParagraphStyle(name='Heading4', fontName='ChineseFont-Slim', fontSize=12, leftIndent=-20, spaceAfter=10,
                    spaceBefore=10, leading=20)

# 定义全局表格样式
tableStyle = TableStyle([
    ('GRID', (0, 1), (-1, -1), 1, '#49A8D8'),  # 定义网格线，从第二行开始
    ('BOX', (0, 0), (-1, -1), 1, '#49A8D8'),  # 整体边框
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # 文本垂直居中
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
cellStyle = styles['Normal'].clone(name='cellStyle', fontName='ChineseFont-Slim', fontSize=10, alignment=0)

# pdf页面：封面、正文
Cover = []
Pages = []
page_header = None


class CanvasDrawing(Flowable):
    """ 绘制首页：一个自定义Flowable，用于在文档中绘制Canvas内容 """

    def __init__(self, info):
        Flowable.__init__(self)
        self.img_path = info['coverPath']
        self.type = info.get('reportType', 'a')
        self.info = info
        self.width = A4[0] - 11
        self.height = A4[1] - 12

    def cover_a(self):
        """ 绘制封面 """
        self.canv.drawImage(self.img_path, -6, 14, width=A4[0], height=A4[1])

        # 绘制标题
        header = self.info.get("deviceName", None) + " 资源明细报告"
        sub = self.info.get("deviceName", None).replace("_", " ") + " RESOURCE DETAILS"
        self.draw_custom_text(header, 0, 570, "center", "ChineseFont-Bold", 30, "#244B98")
        self.draw_custom_text(sub, 0, 600, "center", "ChineseFont-Bold", 14, "#969897")
        self.draw_custom_text("资源名称：" + self.info.get("deviceName", None), 170, (650), "left",
                              "ChineseFont-Bold", 16, "#000000")
        self.draw_custom_text("资源类型：" + self.info.get("deviceType", None), 170, (680), "left",
                              "ChineseFont-Bold", 16, "#000000")
        self.draw_custom_text("资源地址：" + self.info.get("deviceAddress", None), 170, (710), "left",
                              "ChineseFont-Bold", 16, "#000000")

    def cover_b(self):
        """ 绘制封面 """
        self.canv.drawImage(self.img_path, -6, 14, width=A4[0], height=A4[1])
        self.draw_custom_text(self.info.get("reportTime", datetime.now().year),
                              100, 550, "left", "ChineseFont-Bold", 40, "#DF8528")
        self.draw_custom_text(self.info.get("reportName", None),
                              100, 600, "left", "ChineseFont-Bold", 40, "#23548A")

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
                adjusted_page_num = self.page - len(Cover)

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
        self.header_text = page_header

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
        header_x = 55  # 页眉的横向位置，可以根据需要调整
        header_y = A4[1] - 40  # 页眉的纵向位置，可以根据需要调整
        header_font = "ChineseFont-Bold"  # 页眉的字体，可以根据需要调整
        header_font_size = 10  # 页眉的字号，可以根据需要调整
        header_color = "#2F5496"  # 浅蓝色

        # 设置字体和颜色
        self.setFont(header_font, header_font_size)
        self.setFillColor(header_color)

        # 绘制页眉文本
        self.drawString(header_x, header_y, header_text)

        # 绘制同色横线
        line_width = A4[0] - 2 * header_x  # 横线的长度，可以根据需要调整
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
        bar.valueAxis.labels.fontName = 'ChineseFont-Slim'
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
        d.wrapOn(self.canv, self.width, self.height)
        d.drawOn(self.canv, self.x, self.y)


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
        # 半角英文字符和数字
        elif c.isalnum():
            return 0.5 * self.fontSize
        # 其他半角字符（包括半角标点等）
        else:
            return 0.45 * self.fontSize

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
        bar.width = self.width - max_label_width - 30
        bar.x = max_label_width
        bar.y = 0
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
        d.wrapOn(self.canv, self.width, self.height)
        d.drawOn(self.canv, self.x, self.y)


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
        draw = Drawing()

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
        draw.drawOn(self.canv, self.x, self.y)


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
        draw = Drawing()

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
        draw.drawOn(self.canv, self.x, self.y)


class CustomTable:
    def __init__(self, data, merge=None):
        self.data = data
        self.merge = merge

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
        table = Table(rows, rowHeights=([27] + [None] * (len(rows) - 1)), colWidths=480 / columns)
        table.setStyle(tableStyle)
        self.cell_style(table)
        if self.merge:
            self.same_merge(table, rows)
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
                style.fontName = "ChineseFont-Bold" if item.get("isBold") else "ChineseFont-Slim"
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
            skip = 0
            for ci, cell in enumerate(row):
                if cell is not None:
                    table.setStyle(
                        TableStyle([('BACKGROUND', (ci, ri), (ci, ri),
                                     cell.get('background', None))]))
                    # 跳过已经合并的单元格
                    if skip > 0:
                        skip -= 1
                        continue

                    # 处理合并单元格
                    size = cell.get('size', 0)
                    if size > 1:
                        table.setStyle(TableStyle([('SPAN', (ci, ri), (ci + size - 1, ri))]))
                        skip = size - 1

    def same_merge(self, table, items) -> None:
        """
        相邻列行的单元格值相同自动合并，为None也自动合并
        :param table: 表格
        :param items: 数据
        """
        num_rows = len(items)
        num_cols = len(items[0])

        for col in range(num_cols):
            row_start = 0
            while row_start < num_rows:
                row_end = row_start
                while row_end < num_rows - 1:
                    # 提取当前行和下一行的单元格内容
                    current_item = items[row_end][col]
                    next_item = items[row_end + 1][col]

                    # 如果当前单元格和下一个单元格的值相同（或都是 None），则扩展合并范围
                    if (current_item, next_item) == (None, None) or \
                            (
                                    current_item is not None and next_item is not None and current_item.text == next_item.text):
                        row_end += 1
                    else:
                        break

                if row_end > row_start:
                    # 合并从 row_start 到 row_end 的单元格
                    table.setStyle(TableStyle([
                        ('SPAN', (col, row_start), (col, row_end))
                    ]))

                row_start = row_end + 1


# 函数接受数据参数并生成PDF
def build(filename: str, header=None) -> None:
    """
    生成pdf
    :param header:
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
    pdf = CustomTemplate(filename, pagesize=A4)
    global page_header
    page_header = header
    pdf.multiBuild(doc, canvasmaker=NumberPageCanvas)


def addCover(info) -> None:
    """ 添加封面
    :param info: 封面信息
    """
    Cover.append(CanvasDrawing(info))
    Cover.append(PageBreak())


# 设置页面内容
def addContent(body: List[dict]) -> None:
    """ 添加文本内容、List[dict]格式指明标题等级1、2、3为标题、4：为正文
    例：body=[{'level': 1, 'content': "一、一级标题"}]
    :param body: 文本内容
    """
    content_list = [item for item in body if item and item['level'] <= 3]
    Pages.extend(contents(content_list))


def addTitle(name=None, tag=None, color=colors.red, font_size=12, font_color=colors.black, leading=20,
             leftIndent=-20, space=10) -> None:
    if name is None:
        return None
    style = ParagraphStyle(
        'ColoredText',
        parent=styles['Normal'],
        fontName='ChineseFont-Bold',
        font_color=font_color,
        fontSize=font_size,
        leftIndent=leftIndent,
        spaceBefore=space,
        spaceAfter=space,
        leading=leading
    )
    title = f"{name}"
    if tag:
        title = title + f"<font color={color}>{'&nbsp;' * 10}{tag}</font>"
    Pages.append(Paragraph(title, style))


def addParagraph(content: str, font_size=10.5, font_color=colors.black, leading=15, leftIndent=-20,
                 space=5):
    """
     创建一个自动换行的段落
    :param content:
    :param font_size:
    :param font_color:
    :param leading:
    :param leftIndent:
    :param space:
    :return:
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
    for item in text:
        addTitle(item.get("title"), space=3, leftIndent=-10)
        addParagraph(item.get("content"), leftIndent=-10, space=3)


def addTable(table, merge: bool) -> None:
    """ 添加表格
    :param header: 表格表头
    :param table: 表格数据
    :param columnBold: 指定列加粗
    :param conditions: 指定列数据条件判断
    :param merge: 指定列合并单元格
    """
    Pages.append(Spacer(1, 12))
    Pages.append(CustomTable.insert_table(CustomTable(table, merge=merge)))
    Pages.append(Spacer(1, 12))


def addVerticalChart(data: List[dict[str, str]], bars: List[str],
                     label='name', legend=None, colors=None):
    """
    添加柱状图
    :param data: 图表数据
    :param label: 横坐标标签
    :param bars: 柱状图显示数据列表
    :param colors: 柱状图显示数据列颜色列表
    :param legend: 图例说明列表
    :return:
    """
    if colors is None:
        colors = ["#4472C4", "#ED7D31", "#FFC000"]
    Pages.append(VerticalChart(data=data, label=label, bars=bars, color_list=colors, legend=legend))


def addHorizontalChart(data: List[dict[str, str]], bars: List[str],
                       label='name', legend=None, colors=None):
    """
    添加柱状图
    :param data: 图表数据
    :param label: 横坐标标签
    :param bars: 柱状图显示数据列表
    :param colors: 柱状图显示数据列颜色列表
    :param legend: 图例说明列表
    :return:
    """
    if colors is None:
        colors = ["#4472C4", "#ED7D31", "#FFC000"]
    Pages.append(
        HorizontalChart(data, label, bars, colors, legend, font_size=7, label_len_max=220, width=400, height=200))


def addPie(data):
    Pages.append(PieChart(font_name="ChineseFont-Slim", data=data, label_distance=20, radius=50, font_size=8))


def addRing(data, tag=None):
    Pages.append(
        RingChart(font_name="ChineseFont-Slim", data=data, radius=80, font_size=10, tag=tag))


def contents(title) -> List[Paragraph]:
    """
    生成目录
    :param title: 目录内容
    :return: 样式列表
    """
    style = None
    content_list = []
    for item in title:
        if item.get('level') == 1:
            style = h1
        elif item.get('level') == 2:
            style = h2
        elif item.get('level') == 3:
            style = h3
        else:
            style = h4
        style.textColor = item.get("color", colors.black)
        content_list.append(heading(item.get('content'), style))
    return content_list


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
