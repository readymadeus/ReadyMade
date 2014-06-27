from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph

styles = getSampleStyleSheet()
styleN = styles['Normal']
styleH = styles['Heading1']

def footer(canvas, doc):
    canvas.saveState()
    P = Paragraph("This is a multi-line footer.  It goes on every page.  " * 5,
                  styleN)
    w, h = P.wrap(doc.width, doc.bottomMargin)
    P.drawOn(canvas, doc.leftMargin, h)
    canvas.restoreState()

doc = BaseDocTemplate('test.pdf', pagesize=letter)
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
               id='normal')
template = PageTemplate(id='test', frames=frame, onPage=footer)
doc.addPageTemplates([template])

text = []
for i in range(111):
    text.append(Paragraph("This is line %d." % i,
                          styleN))
doc.build(text)