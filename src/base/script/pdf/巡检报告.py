from hashlib import sha1
from typing import List

import pandas as pd
from reportlab.lib import pagesizes
from reportlab.lib.styles import ParagraphStyle as PS, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import TableStyle, Paragraph, PageBreak, BaseDocTemplate, PageTemplate, Table
from reportlab.platypus.frames import Frame
from reportlab.platypus.tableofcontents import TableOfContents

# 注册字体
pdfmetrics.registerFont(TTFont('ChineseFont', 'font/SimSun.ttf'))
pdfmetrics.registerFont(TTFont('ChineseFont-Bold', 'font/微软雅黑粗体.ttf'))

# 目录样式
ContentStyle = PS(name='centered', fontName='ChineseFont-Bold', fontSize=17, leftIndent=-10, leading=12, spaceAfter=10,
                  textColor="#365F91")
ContentsStyle = [
    PS(fontName='ChineseFont', fontSize=10, name='TOCHeading1', leading=12, leftIndent=-10),
    PS(fontName='ChineseFont', fontSize=10, name='TOCHeading2', leading=12, leftIndent=0),
    PS(fontName='ChineseFont', fontSize=10, name='TOCHeading3', leading=12, leftIndent=10)
]

# 定义1-4级标题样式
h1 = PS(name='Heading1', fontName='ChineseFont-Bold', fontSize=16, leftIndent=-5, spaceBefore=10, leading=20)
h2 = PS(name='Heading2', fontName='ChineseFont-Bold', fontSize=14, leftIndent=-5, spaceBefore=10, leading=20)
h3 = PS(name='Heading3', fontName='ChineseFont-Bold', fontSize=12, leftIndent=-5, spaceBefore=10, leading=20)
h4 = PS(name='Heading4', fontName='ChineseFont', fontSize=12, leftIndent=-5, spaceBefore=10, leading=20)

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
    ('FONTNAME', (0, 1), (-1, 1), 'ChineseFont-Bold'),  # 第二行字体加粗
    ('FONTNAME', (0, 2), (-1, -1), 'ChineseFont'),  # 其他行使用注册的中文字体
    ('FONTSIZE', (-1, 0), (-1, -1), 10),  # 字体大小
    ('LINEABOVE', (0, 0), (-1, 0), 1.5, '#49A8D8'),  # 首行上方线条加粗
    ('LINEBELOW', (0, -1), (-1, -1), 1.5, '#49A8D8'),  # 尾行下方线条加粗
    ('LINEBEFORE', (0, 0), (0, -1), 0, '#FFFFFF'),  # 设置第一列左边框为白色
    ('LINEAFTER', (-1, 0), (-1, -1), 0, '#FFFFFF'),  # 设置最后一列右边框为白色
])


# 定义页面模板样式
class CustomTemplate(BaseDocTemplate):
    def __init__(self, filename, **kw):
        super().__init__(filename, **kw)
        template = PageTemplate('normal', [Frame(20 * mm, 23 * mm, 170 * mm, 250 * mm, id='F1')])
        self.addPageTemplates(template)

    def afterFlowable(self, flowable):
        if flowable.__class__.__name__ == 'Paragraph':
            text = flowable.getPlainText()
            style = flowable.style.name
            if style == 'Heading1':
                level = 0
            elif style == 'Heading2':
                level = 1
            elif style == 'Heading3':
                level = 2
            else:
                return
            e = [level, text, self.page]
            bn = getattr(flowable, '_bookmarkName', None)
            if bn is not None: e.append(bn)
            self.notify('TOCEntry', tuple(e))


# 定义页面页码样式
class NumberPageCanvas(Canvas):
    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)
        self.pages = 0  # 初始化页面计数器

    def showPage(self):
        self.pages += 1  # 页面计数器加一
        self.draw_page_number(self.pages)  # 为当前页面添加页码
        Canvas.showPage(self)

    def draw_page_number(self, page_number):
        # 绘制阴影矩形
        self.setFillColor("#808080")
        self.rect(180 * mm, 10 * mm, 12 * mm, 6 * mm, fill=True, stroke=False)
        # 绘制间隙矩形
        self.setFillColor("#FFFFFF")
        self.rect(180 * mm, 10.5 * mm, 12 * mm, 6 * mm, fill=True, stroke=False)
        # 绘制主矩形
        self.setFillColor("#2AB4E9")
        self.rect(180 * mm, 11.5 * mm, 12 * mm, 6 * mm, fill=True, stroke=False)
        # 设置页码文字样式（占两位字符）
        self.setFillColor("#FFFFFF")
        self.setFont("Helvetica-Bold", 14)
        self.drawString(183.5 * mm, 13 * mm, "{:02d}".format(page_number))


# pdf页面
Pages = []


# 函数接受数据参数并生成PDF
def build(filename: str) -> None:
    """
    生成pdf
    :param filename: 指定文件路径文件名
    """
    toc = TableOfContents()
    toc.levelStyles = ContentsStyle
    toc.dotsMinLevel = 0
    Pages.insert(0, Paragraph('目录', ContentStyle))
    Pages.insert(1, toc)
    Pages.insert(2, PageBreak())
    pdf = CustomTemplate(filename, pagesize=pagesizes.A4)
    pdf.multiBuild(Pages, canvasmaker=NumberPageCanvas)


# 设置页面内容
def addText(body: List[dict[str, str]]) -> None:
    """ 添加文本内容
    :param body: 文本内容
    """
    Pages.extend(contents(body))


def addTable(header: str, table: List[dict], ignoreSubRow: bool = False,
             conditions: List[dict] = None, merge: List[str] = None) -> None:
    """ 添加表格
    :param header: 表格表头
    :param table: 表格数据
    :param ignoreSubRow: 是否忽略次级表头
    :param conditions: 指定列数据条件判断
    :param merge: 指定列合并单元格
    """
    Pages.append(insertTable(header, table, ignoreSubRow=ignoreSubRow, conditions=conditions, merge=merge))


# 生成标题和目录
def contents(title):
    return [
        heading(item.get('content'),
                h1 if item.get('level') == 1 else h2 if item.get('level') == 2 else h3 if item.get(
                    'level') == 3 else h4)
        for item in title
    ]


# 生成目录和标题关联链接
def heading(text, style):
    bn = sha1((text + style.name).encode()).hexdigest()
    h = Paragraph(text + '<a name="%s"/>' % bn, style)
    h._bookmarkName = bn
    return h


# 插入表格内容
def insertTable(header, data, ignoreSubRow=False, conditions=None, merge=None):
    rows = []
    # 次行表头、表头
    subRow = list(data[0].keys())
    headerRow = [header] + [""] * (len(subRow) - 1)

    # 读取json数据转换为列表
    items = pd.DataFrame(data).values.tolist()
    # 保存一份原始数据，用于cell_style、merge_cells
    originalItems = [list(row) for row in items]
    # 使用Paragraph自动换行，并仅处理字符串类型的数据
    styles = getSampleStyleSheet()
    for row in items:
        for i, item in enumerate(row):
            if isinstance(item, str):
                # 使用自定义中文字体和样式
                paragraph_style = styles['Normal'].clone(name='a', fontName='ChineseFont', fontSize=10)
                row[i] = Paragraph(item, paragraph_style)

    # 组装表格
    rows.append(headerRow)
    if not ignoreSubRow:
        rows.append(subRow)
    rows.extend(items)
    # 创建表格, 固定首行行高，其余行行高自适应
    table = Table(rows, rowHeights=([27] + [None] * (len(rows) - 1)), colWidths=170 * mm / len(subRow))

    # 设置全局表格样式
    table.setStyle(tableStyle)
    cellStyle(table, conditions, subRow, originalItems)
    mergeCells(table, merge, subRow, originalItems)
    return table


# 定义单元格样式
def cellStyle(table, conditions, sub_row, items):
    if conditions is None:
        return
    for element in conditions:
        for i, item in enumerate(items):
            for j, cell in enumerate(item):
                if sub_row[j] == element.get('column') and element.get('expression')(cell):
                    table.setStyle(TableStyle([('BACKGROUND', (j, i + 2), (j, i + 2), element.get('color'))]))


# 处理合并单元格
def mergeCells(table, merge, sub_row, items):
    if merge is None:
        return
    for mergeColumn in merge:
        if mergeColumn in sub_row:
            columnIndex = sub_row.index(mergeColumn)
            startRow = None
            prev_value = 'unique_nonexistent_value'  # 初始值设为一个唯一的值
            for rowIndex, row_data in enumerate(items):
                currentValue = row_data[columnIndex]
                # 如果当前值是 None，将其视为一个特殊标记
                if currentValue is None:
                    currentValue = 'special_null_value'
                if currentValue != prev_value:
                    if startRow is not None and rowIndex - startRow > 1:
                        table.setStyle(
                            TableStyle([('SPAN', (columnIndex, startRow + 2), (columnIndex, rowIndex + 1))]))
                    startRow = rowIndex
                prev_value = currentValue
            # 检查并处理最后一个合并区域
            if startRow is not None and len(items) - startRow > 1:
                table.setStyle(TableStyle([('SPAN', (columnIndex, startRow + 2), (columnIndex, len(items) + 1))]))
