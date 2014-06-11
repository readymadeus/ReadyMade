import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import matplotlib.image as mpimg
import os

def scatter(x,y,count,xlabel,ylabel,plotpath,vartype,coeff):
	fig=plotpath+str(count)+".png"
	filename="scatter"+str(count)+".png"
	figure=plt.figure()
	ax=figure.add_subplot(111)
	ax.scatter(x,y)
	if vartype=="control":
		title="Input and Control Variables"
	else:
		title=vartype+" Variables"
	ax.set_title(title)
	ax.set_xlabel(xlabel)
	ax.set_ylabel(ylabel)
	figure.text(0.5,0.6,"Correlation Coefficient: "+str(coeff), fontsize=14)
	figure.savefig(fig)
	return filename