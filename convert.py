import csv
import re,os
import pandas as pd
import numpy as np

def transform(csvfilename):
	pattern='([a-zA-Z0-9_]+?)\.'
	print csvfilename
	csvfile = open(csvfilename, 'rU')
	filename=re.findall(pattern,csvfilename)[0]
	csvf=pd.read_csv(csvfilename)
        for col in csvf.columns:
          col_dtype = csvf[col].dtype
          if not (col_dtype in (np.float64, np.int64)):
            print col + " non-numeric and rejected."
            del csvf[col]
	return csvf

def test(csvfilename):
	pattern='([a-zA-Z0-9_]+?)\.'
	print csvfilename
	csvfile=pd.read_csv(csvfilename)
	print csvfile

'''


Step#1: What is the index you want to set?
If none, default will be chosen

Step#2: Select input, control, output variables.

Step#3: Show correlations between controls and input variable.
If any of the correlations are higher than 0.6, ask user if they're sure they wanna use both the variables.

Question for Clair: Ask the user about only one input at a time

Optional: Understand this later
Step#4: Once the variables are chosen, run linear regressions using the forward method.
Add controls one by one.

'''

if __name__=='__main__':
	test('./static/files/uploads/dhs_cell.csv')
