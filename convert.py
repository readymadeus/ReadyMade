import csv
import json
import re,os

def csv_to_json(csvfilename,folder):
	pattern='([a-zA-Z0-9_]+?)\.'
	csvfile = open(csvfilename, 'rU')
	filename=re.findall(pattern,csvfilename)[0]
	filepath=os.path.join(folder, filename)
	jsonfile = open(filepath+".json", 'w')
	r=csv.reader(csvfile)
	fieldnames=r.next()
	fieldnames=[f.replace(' ','_') for f in fieldnames]
	fieldnames=tuple(fieldnames)
	reader = csv.DictReader(csvfile, fieldnames)
	jsonfile.write("jsondat=[")
	for row in reader:
	    json.dump(row, jsonfile)
	    jsonfile.write(',\n')
	jsonfile.write("]")

if __name__=='__main__':
	csv_to_json('coffeedat.csv','./static/files/uploads')