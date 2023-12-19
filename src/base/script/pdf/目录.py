from hashlib import sha1

from reportlab.lib.styles import ParagraphStyle as PS
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, PageBreak, BaseDocTemplate, PageTemplate
from reportlab.platypus.frames import Frame
from reportlab.platypus.tableofcontents import TableOfContents

# 注册字体
pdfmetrics.registerFont(TTFont('ChineseFont-Bold', 'font/微软雅黑粗体.ttf'))

# 目录样式
contents_style = [
    PS(fontName='ChineseFont', fontSize=16, name='TOCHeading1', leftIndent=10, firstLineIndent=-20, spaceBefore=10,
       leading=16),
    PS(fontName='ChineseFont', fontSize=14, name='TOCHeading2', leftIndent=20, firstLineIndent=-20, spaceBefore=5,
       leading=14),
    PS(fontName='ChineseFont', fontSize=12, name='TOCHeading3', leftIndent=30, firstLineIndent=-20, spaceBefore=5,
       leading=12)
]

# 定义标题样式
h1 = PS(name='Heading1', fontName='ChineseFont-Bold', fontSize=16,
        leftIndent=-20, spaceBefore=15, spaceAfter=15, leading=15)

h2 = PS(name='Heading2', fontName='ChineseFont-Bold', fontSize=14,
        leftIndent=-20, spaceBefore=15, spaceAfter=15, leading=15)

h3 = PS(name='Heading3', fontName='ChineseFont-Bold', fontSize=12,
        leftIndent=-20, spaceBefore=15, spaceAfter=15, leading=15)

h4 = PS(name='Heading4', fontName='ChineseFont-Bold', fontSize=10,
        leftIndent=-20, spaceBefore=15, spaceAfter=15, leading=15)

# 定义页面模板样式
class MyDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kw):
        super().__init__(filename, **kw)
        # self.allowSplitting = 0
        template = PageTemplate('normal', [Frame(2.5 * cm, 2.5 * cm, 15 * cm, 25 * cm, id='F1')])
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
            E = [level, text, self.page]
            bn = getattr(flowable, '_bookmarkName', None)
            if bn is not None: E.append(bn)
            self.notify('TOCEntry', tuple(E))



# 生成标题和目录
def set_contents(title):
    story = []
    toc = TableOfContents()
    toc.levelStyles = contents_style
    story.append(toc)
    story.append(PageBreak())
    # 设置目录级别
    story.extend([
        doHeading(item.get('content'), h1 if item.get('level') == 1 else h2 if item.get('level') == 2 else h3 if item.get('level') == 3 else h4)
        for item in title
    ])
    return story


# 生成目录和标题关联链接
def doHeading(text, sty):
    bn = sha1((text + sty.name).encode()).hexdigest()
    h = Paragraph(text + '<a name="%s"/>' % bn, sty)
    h._bookmarkName = bn
    return h


