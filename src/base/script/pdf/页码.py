from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas


class NumberedCanvas(Canvas):
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
        self.rect(180*mm, 10*mm, 12*mm, 6*mm, fill=True, stroke=False)
        # 绘制间隙矩形
        self.setFillColor("#FFFFFF")
        self.rect(180*mm, 10.5*mm, 12*mm, 6*mm, fill=True, stroke=False)
        # 绘制主矩形
        self.setFillColor("#2AB4E9")
        self.rect(180*mm, 11.5*mm, 12*mm, 6*mm, fill=True, stroke=False)
        # 设置页码文字样式
        self.setFillColor("#FFFFFF")
        self.setFont("Helvetica-Bold", 14)
        self.drawString(184*mm, 13*mm, str(page))
