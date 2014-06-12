from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import landscape
from datetime import date
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image,BaseDocTemplate, Frame,Paragraph, Table, TableStyle, PageTemplate
from reportlab.lib import colors
import config,random

def create_pdf(data):
	report_header=config.ROOT_PATH+'/static/images/report-header.jpg'
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
	regdata=data[10]
	#File Name
	pdfname=config.ROOT_PATH+"/static/files/uploads/RM_Report_"+pname+"_"+today+".pdf"
	pdfilename="/static/files/uploads/RM_Report_"+pname+"_"+today+".pdf"
	report = []
	#File Name
	doc=BaseDocTemplate(pdfname,pagesize=letter)
	frame=Frame(doc.leftMargin,doc.bottomMargin,doc.width,doc.height,id='normal')
	template=PageTemplate(id='test',frames=frame)
	doc.addPageTemplates([template])
	styles = getSampleStyleSheet()
	#Report Header
	header_img=Image(report_header)
	report.append(header_img)

	#Title
	title="ReadyMade Analysis Report"
	report.append(Paragraph(title,styles['Heading1']))
	analysis="Analysis on: "+today
	report.append(Paragraph(analysis,styles['Normal']))
	#Introduction String
	report.append(Paragraph("Introduction",styles['Heading2']))
	intro="The organization "+orgname+" used ReadyMade in order to conduct an impact analysis for their project "+ pname+". The mission of "+orgname+" is "+mission+". "+orgname+" serves its mission by providing "+product+" to their primary user group - '"+puser+"'."
	report.append(Paragraph(intro,styles['Normal']))
	
	#Key Impact Question
	report.append(Paragraph("Key Impact Question",styles['Heading2']))
	impact="\" What is the relationship between "+product+" and the project's ability to achieve their intended outcomes? \"" 
	report.append(Paragraph(impact,styles['Normal']))

	#Data & Methods String
	report.append(Paragraph("Data & Methods",styles['Heading2']))
	report.append(Paragraph("Identifying Key Variables",styles['Heading3']))
	methods="In keeping with the ReadyMade tenet to keep the analysis simple, we look for one key outcome variable that is highly correlated with the other available outcome variables "
	metext = Paragraph(methods,styles['Normal'])
	report.append(metext)

	#Correlation
	report.append(Paragraph("Correlations between variables",styles['Heading2']))
	for plot in plots:
		plot_img=Image(plot,width=200,height=200)
		report.append(plot_img)
	plot_text="Therefore, we narrowed our investigation to one key performance variable, "+outputs+", which provides similar results as using any of the other available outcomes variables (confirmed by our statistical analysis). Similarly, We also decided to use only "+inputs+" for input variables and "+controls+" to control for environmental characteristics."
	report.append(Paragraph(plot_text,styles['Normal']))

	#Regression
	report.append(Paragraph("Regression Analysis",styles['Heading2']))
	for regs in regdata:
		contents=[]
		formula=regs[0]
		r2=regs[1]
		fstat=regs[2]
		pvalue=regs[3]
		df=regs[4]
		nobs=regs[5]
		report.append(Paragraph("What are we measuring?",styles['Heading3']))
		reg_stats="<p>"+formula+"<br/><br/>R-Squared: "+str(r2)+"<br/>F-Stat: "+str(fstat)+"<br/>p-Value: "+str(pvalue)+"<br/>Degrees of Freedom: "+str(df)+"<br/>No. of observations: "+str(nobs)+"<br/><br/></p>"
		report.append(Paragraph(reg_stats,styles['Normal']))
		theader=["  ","Coefficient","p-Value","Std Error","t-stat"]
		contents.append(theader)
		inputData=regs[6]
		for idata in inputData:
			contents.append(idata)
		controlData=regs[7]
		for cdata in controlData:
			contents.append(cdata)
		table = Table(contents)
		table.setStyle(TableStyle([
	                       ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
	                       ('BOX', (0,0), (-1,-1), 0.25, colors.black),
	                       ]))
		report.append(table)
		if pvalue<0.01:
			if r2>0:
				polarity="positive"
				change="increase"
			else:
				polarity="negative"
				change="decrease"
			conclusion="The regression indicates that "+ str(orgname)+" "+str(product)+" have a "+polarity+" relationship with "+pname+" inputs: Every 1 unit of "+orgname+" "+product+" to "+pname+" is associated with a(n) "+change+" of "+str(r2)+" units in "+orgname+" inputs."
		else:
			conclusion="The regression indicates that "+ str(orgname)+" "+str(product)+" do not have a significant relationship with "+pname+"\'s inputs i.e any change in the units of "+orgname+" "+product+"\'s to "+pname+" is not associated with any change of units in "+orgname+"\'s inputs."
		report.append(Paragraph("Conclusion",styles['Heading3']))
		report.append(Paragraph(conclusion,styles['Normal']))
	print 'writing into pdf file'
	doc.build(report)
	return pdfilename


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
	reglist=[[u'Measuring the impact of "Amount of RC working capital loan (US$) disbursed" on "Purchases from rural producers (US$) - adjusted" while controlling for variables such as "Number of suppliers, Number of suppliers (with 5,000 member cap), Country daily minimum wage"', 0.35, 13.82, 0.0, 5, 98, [[u'Amount of RC working capital loan (US$) disbursed', 3.0675, 0.0, 0.65, 4.73]], [[u'Number of suppliers', -45.6936, 0.1575, 32.07, -1.42], [u'Number of suppliers (with 5,000 member cap)', 709.5482, 0.0007, 202.71, 3.5], [u'Country daily minimum wage', 97276.7619, 0.1021, 58925.61, 1.65]]]]
	data.append(reglist)
	create_pdf(data)