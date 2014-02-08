import os
from flask import Flask

app=Flask(__name__)

@app.route('/')
def hello():
	return render_template("rm_intro.html")

@app.route('/interview')
def questionnaire():
	return render_template("qanda1.html")

if __name__=="__main__":
	app.run(port=8080)