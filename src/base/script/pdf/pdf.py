from  reportlab.lib.styles import ParagraphStyle as PS
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.platypus.frames import Frame
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.tableofcontents import TableOfContents


class MyDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kw):
        super().__init__(filename, **kw)
        self.allowSplitting = 0
        template = PageTemplate('normal', [Frame(25*mm, 2.5*mm, 200*mm, 280*mm, id='F1')])
        self.addPageTemplates(template)

    def afterFlowable(self, flowable):
        "Registers TOC entries."
        if flowable.__class__.__name__ == 'Paragraph':
            text = flowable.getPlainText()
            style = flowable.style.name
            if style == 'Heading1':
                level = 0
            elif style == 'Heading2':
                level = 1
            else:
                return
            E = [level, text, self.page]
            #if we have a bookmark name append that to our notify data
            bn = getattr(flowable,'_bookmarkName',None)
            if bn is not None: E.append(bn)
            self.notify('TOCEntry', tuple(E))

centered = PS(name = 'centered',
              fontSize = 30,
              leading = 16,
              alignment = 1,
              spaceAfter = 20)

h1 = PS(
    name = 'Heading1',
    fontSize = 14,
    leading = 16)


h2 = PS(name = 'Heading2',
        fontSize = 12,
        leading = 14)


# Build story.
story = []

# Create an instance of TableOfContents. Override the level styles (optional)
# and add the object to the story

toc = TableOfContents()
toc.levelStyles = [
    PS(fontName='Times-Bold', fontSize=20, name='TOCHeading1', leftIndent=20, firstLineIndent=-20, spaceBefore=10, leading=16),
    PS(fontSize=18, name='TOCHeading2', leftIndent=40, firstLineIndent=-20, spaceBefore=5, leading=12),
]
story.append(toc)

#this function makes our headings
def doHeading(text,sty):
    from hashlib import sha1
    #create bookmarkname
    bn = sha1((text + sty.name).encode()).hexdigest()
    #modify paragraph text to include an anchor point with name bn
    h=Paragraph(text+'<a name="%s"/>' % bn,sty)
    #store the bookmark name on the flowable so afterFlowable can see this
    h._bookmarkName=bn
    story.append(h)

story.append(Paragraph('<b>Table of contents</b>', centered))
story.append(PageBreak())
doHeading('First heading', h1)
story.append(Paragraph('Text in first heading', PS('body')))
doHeading('First sub heading', h2)
story.append(Paragraph('Text in first sub heading', PS('body')))
story.append(PageBreak())
doHeading('Second sub heading', h2)
story.append(Paragraph('Text in second sub heading', PS('body')))
story.append(PageBreak())
doHeading('Last heading', h1)
story.append(Paragraph('Text in last heading', PS('body')))
doc = MyDocTemplate('out/目录.pdf')
doc.multiBuild(story)