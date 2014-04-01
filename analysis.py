import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import matplotlib.image as mpimg
import os

def scatter(x,y,count,xlabel,ylabel,plotpath):
	fig=plotpath+str(count)+".png"
	figure=plt.figure()
	ax=figure.add_subplot(111)
	ax.scatter(x,y)
	title="Plot #"+str(count)
	ax.set_title(title)
	ax.set_xlabel(xlabel)
	ax.set_ylabel(ylabel)
	figure.savefig(fig)
	return fig