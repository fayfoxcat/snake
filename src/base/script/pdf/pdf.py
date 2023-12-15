from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, TableOfContents, PageBreak
from reportlab.platypus import Paragraph, Spacer, Table, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# 创建一个PDF文档
doc = SimpleDocTemplate("document_with_table_of_contents.pdf", pagesize=landscape(letter))

# 创建样式
styles = getSampleStyleSheet()
toc_style = styles["Normal"]
toc_style.alignment = 1  # 居中对齐

# 创建目录
toc = TableOfContents()
toc.setStyle(toc_style)
toc.addEntry(0, "Cover Page", 1)
toc.addEntry(1, "Chapter 1", 2)
toc.addEntry(1, "Chapter 2", 3)

# 创建页面模板
def landscape_page_template(canvas, doc, content_frame):
    width, height = landscape(letter)
    canvas.saveState()
    canvas.setFont("Helvetica", 10)
    canvas.drawString(inch, height - inch, "Page %d" % doc.page)
    canvas.restoreState()

landscape_template = PageTemplate(id="landscape", frames=[content_frame], onPage=landscape_page_template)

# 创建内容
content = []

# 封面页
cover_page = Paragraph("Cover Page", styles["Title"])
content.append(cover_page)
content.append(PageBreak())

# 第一章
chapter1 = Paragraph("Chapter 1", styles["Heading1"])
content.append(chapter1)
content.append(Spacer(1, inch))

# 在此添加第一章内容

# 第二章
chapter2 = Paragraph("Chapter 2", styles["Heading1"])
content.append(chapter2)
content.append(Spacer(1, inch))

# 在此添加第二章内容

# 添加目录到文档
content.insert(0, toc)
doc.addPageTemplates([landscape_template])
doc.build(content)
