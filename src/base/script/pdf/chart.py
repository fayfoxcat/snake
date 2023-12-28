#!/bin/env python
# -*- coding: UTF-8 -*-
"""
方法用于生成pdf，依次需求调用cover反复调用 addText addTable构建pdf页面，调用build生成pdf文档
"""
import math
from hashlib import sha1
from typing import List

from reportlab.graphics.charts.barcharts import VerticalBarChart, BarChartProperties, HorizontalBarChart
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.renderSVG import cos, pi, sin
from reportlab.graphics.shapes import Drawing, String, Line, Circle
from reportlab.graphics.widgetbase import TypedPropertyCollection
from reportlab.lib import pagesizes, colors
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph, PageBreak, PageTemplate, SimpleDocTemplate, Flowable
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
    def __init__(self, data, x=0, y=0, radius=80, font_name=None, font_size=10, label_distance=None):
        Flowable.__init__(self)
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
            label_text = f'{item["name"]} ({item["cont"]})'

            # 计算每个扇形的中点角度
            angle = (item["cont"] / total) * 360
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
        draw.drawOn(self.canv, self.x, self.y)


class RingChart(PieChart):
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
            pie.slices[i].strokeColor = colors.white
            pie.slices[i].strokeWidth = 2

        # 绘制覆盖饼图的同心圆
        circle = Circle(cx=self.radius + pie.x, cy=self.radius + pie.y, r=self.radius / 2,
                        fillColor=colors.white, strokeColor=colors.white)

        draw.add(pie)
        # 设置标签
        self.generate_label(pie, draw)
        draw.add(circle)
        draw.drawOn(self.canv, self.x, self.y)


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


def addVerticalChart(data: List[dict[str, str]], label: str, bars: List[str], colors: List[str], legend: List[str]):
    """
    添加柱状图
    :param data: 图表数据
    :param label: 横坐标标签
    :param bars: 柱状图显示数据列表
    :param colors: 柱状图显示数据列颜色列表
    :param legend: 图例说明列表
    :return:
    """
    Pages.append(VerticalChart(data=data, label=label, bars=bars, color_list=colors, legend=legend))


def addHorizontalChart(data: List[dict[str, str]], label: str, bars: List[str], colors: List[str], legend: List[str]):
    """
    添加柱状图
    :param data: 图表数据
    :param label: 横坐标标签
    :param bars: 柱状图显示数据列表
    :param colors: 柱状图显示数据列颜色列表
    :param legend: 图例说明列表
    :return:
    """
    Pages.append(
        HorizontalChart(data, label, bars, colors, legend, font_size=7, label_len_max=220, width=400, height=200))


def addPie(data):
    Pages.append(PieChart(font_name="ChineseFont-Slim", data=data, label_distance=20, radius=50, font_size=8))


def addRing(data):
    Pages.append(RingChart(font_name="ChineseFont-Slim", data=data))


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
