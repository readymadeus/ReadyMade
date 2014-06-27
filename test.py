from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import landscape
from reportlab.platypus import Image
from datetime import date
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import BaseDocTemplate, Frame,Paragraph, Table, TableStyle, PageTemplate

def footer(canvas, doc):
    canvas.saveState()
    P = Paragraph("ReadyMade Report",
                  styleN)
    w, h = P.wrap(doc.width, doc.bottomMargin)
    P.drawOn(canvas, doc.leftMargin, h)
    canvas.restoreState()

def create_pdf(data):
	report_header='./static/images/report-header.jpg'
	other_header='./static/images/report-header2.jpg'
	today=data[0]
	pname=data[1]
	orgname=data[2]
	mission=data[3]
	product=data[4]
	puser=data[5]
	inputs=data[6]
	outputs=data[7]
	controls=data[8]
	plots=data[9]
	regs=data[10]
	reporttext = []
	#File Name
	pdfname="hello"+pname+"_"+today
	doc=BaseDocTemplate(pdfname,pagesize=letter)
	frame=Frame(doc.leftMargin,doc.bottomMargin,doc.width,doc.height,id='normal')
	template=PageTemplate(id='test',frames=frame,onPage=footer)
	doc.addPageTemplates([template])
	styles = getSampleStyleSheet()
	methods="In keeping with the ReadyMade tenet to keep the analysis simple, we look for one key outcome variable that is highly correlated with the other available outcome variables "
	reporttext.append(Paragraph(methods,styles['Normal']))
	doc.build(metext)
	return pdfname

if __name__=='__main__':
	data=[]
	today=date.today()
	data.append(str(today))
	data.append("projname")
	data.append("orgname")
	data.append("mission")
	data.append("prods")
	data.append("Priya")
	data.append("loans")
	data.append("purchases")
	data.append("suppliers,min wage")
	plots=['../static/images/plots/output/scatter0.png', u'../static/images/plots/input/scatter0.png']
	data.append(plots)
	regs='\n-------------------------Summary of Regression Analysis-------------------------\n\nFormula: Y ~ <A> + <B> + <C> + <intercept>\n\nNumber of Observations:         104\nNumber of Degrees of Freedom:   4\n\nR-squared:         0.4275\nAdj R-squared:     0.4103\n\nRmse:          359659.9429\n\nF-stat (3, 100):    12.8884, p-value:     0.0000\n\nDegrees of Freedom: model 3, resid 100\n\n-----------------------Summary of Estimated Coefficients------------------------\n      Variable       Coef    Std Err     t-stat    p-value    CI 2.5%   CI 97.5%\n--------------------------------------------------------------------------------\n             A     0.0601     0.0215       2.79     0.0063     0.0179     0.1023\n             B    -0.0677     0.0250      -2.71     0.0079    -0.1108    -0.0187\n             C     0.1477     0.0357       4.14     0.0001     0.0778     0.2176\n     intercept 214477.0189 43334.6676       4.95     0.0000 129541.0705 299412.9673\n---------------------------------End of Summary---------------------------------\n'
	reglist=['\n', '-------------------------Summary of Regression Analysis-------------------------\n', '\n', 'Formula: Y ~ <i> + <Country daily minimum wage>\n', '             + <Number of suppliers (with 5,000 member cap)> + <price/farmgate price> + <intercept>\n', '\n', 'Number of Observations:         45\n', 'Number of Degrees of Freedom:   5\n', '\n', 'R-squared:         0.4480\n', 'Adj R-squared:     0.3928\n', '\n', 'Rmse:          615721.5773\n', '\n', 'F-stat (4, 40):     8.1109, p-value:     0.0001\n', '\n', 'Degrees of Freedom: model 4, resid 40\n', '\n', '-----------------------Summary of Estimated Coefficients------------------------\n', '      Variable       Coef    Std Err     t-stat    p-value    CI 2.5%   CI 97.5%\n', '--------------------------------------------------------------------------------\n', '             i     2.4518     0.4953       4.95     0.0000     1.4811     3.4225\n', 'Country daily minimum wage -15986.1562 22155.4115      -0.72     0.4748 -59410.7628 27438.4504\n', 'Number of suppliers (with 5,000 member cap)   309.8408   172.5940       1.80     0.0802   -28.4434   648.1250\n', 'price/farmgate price -152028.4745 111084.0106      -1.36     0.1811 -370929.1471 66872.1981\n', '     intercept 582707.5112 333930.9712       1.74     0.0887 -71797.1948 1237212.2171\n', '---------------------------------End of Summary---------------------------------\n']
	data.append(reglist)
	create_pdf(data)