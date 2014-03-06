import csv
import json
import re,os
import pandas as pd

def transform(csvfilename,folder):
	pattern='([a-zA-Z0-9_]+?)\.'
	print csvfilename
	csvfile = open(csvfilename, 'rU')
	filename=re.findall(pattern,csvfilename)[0]
	filepath=os.path.join(folder, filename)
	jsonfile = open(filepath+".json", 'w')
	r=csv.reader(csvfile,delimiter=' ')
	fieldnames=r.next()
	print fieldnames
	fieldnames=[f.replace(' ','_') for f in fieldnames]
	fieldnames=tuple(fieldnames)
	reader = csv.DictReader(csvfile, fieldnames)
	jsonfile.write("jsondat=[")
	for row in reader:
	    json.dump(row, jsonfile)
	    jsonfile.write(',\n')
	jsonfile.write("]")

def test(csvfilename):
	pattern='([a-zA-Z0-9_]+?)\.'
	print csvfilename
	csvfile=pd.read_csv(csvfilename)
	print csvfile


if __name__=='__main__':
	test('./static/files/uploads/dhs_cell.csv')