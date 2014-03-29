import os
import models
from flask import Flask, request, render_template, redirect, url_for, flash, Blueprint,make_response,session
from flask.ext.login import (LoginManager, current_user, login_required,
							login_user, logout_user, UserMixin,
							confirm_login, fresh_login_required)
try:
	from flask.ext.login import AnonymousUser
except:
	from flask.ext.login import AnonymousUserMixin as AnonymousUser
from flask.ext.sqlalchemy import SQLAlchemy
import models
from database import db_session, init_db, insertUsers,queryUser
from models import User
import traceback
from werkzeug import secure_filename
import csv 
import convert,analysis
import numpy as np
from models import User, Project, Input, Control, Output, Analysis
import traceback
import pandas as pd
import StringIO as sio
import config

app=Flask(__name__)
UPLOAD_FOLDER=config.ROOT_PATH+'/static/files/uploads'
LOG_FILE=config.ROOT_PATH+'/app.log'
ALLOWED_EXTENSIONS=set(['csv'])
current_dir=os.getcwd()
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
username=""

import sys


if not app.debug:
	import logging
	from logging.handlers import RotatingFileHandler
	rfh=RotatingFileHandler(LOG_FILE,mode='a',maxBytes=1024*1024*100,backupCount=5)
	app.logger.addHandler(rfh)
	formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
	rfh.setFormatter(formatter)

# Utility
util = Blueprint('util', __name__, url_prefix='/util')

@util.route('/db/create-all/')
def db_create_all():
	init_db()
	return 'Tables created'

@util.route('/db/test/')
def test_insert():
	insertUsers()
	return "sucess tested"

@util.route('/db/query/')
def test_query():
	queryUser('priya','iyer')
	return "sucess"

app.register_blueprint(util)

class User(UserMixin):
	def __init__(self, name, id, active=True):
		self.name = name
		self.id = id
		self.active = active

	def is_active(self):
		return self.active


class Anonymous(AnonymousUser):
	name = u"Anonymous"


SECRET_KEY = "yeah, not actually a secret"
DEBUG = True

app.config.from_object(__name__)

login_manager = LoginManager()

login_manager.anonymous_user = Anonymous
login_manager.login_view = "login"
#login_manager.login_message = u"Please log in to access this page."
login_manager.refresh_view = "reauth"
login_manager.setup_app(app)

@app.route('/')
def hello():
	return render_template("rm_intro.html")

@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "POST" and "username" in request.form:
		username = str(request.form["username"])
		password = str(request.form["password"])
		project=[]
		userfound=False;
		from models import Project, User
		u=User.query.filter(User.username==username).filter(User.password==password).first()
		if u is not None:
			userfound=True
			session["userid"] = u.id
			session["username"]=u.username
		if userfound:
			session["userid"] = u.id
			remember = request.form.get("remember", "no") == "yes"
			projects=Project.query.filter(Project.userid==u.id).all()
			if projects is not None:
				projs=[]
				pids=[]
				for p in projects:
					projs.append(p)
					pids.append(p.id)
			else:
				pids=[]
				projs=[]    
			return render_template("projects.html",username=u.username,projects=projs)
		else:
			flash(u"Invalid username.")
	return render_template("rm_main.html")

@app.route("/logout", methods=["GET", "POST"])
def logout():
	session.pop("vars",None)
	session.pop("type",None)
	app.secret_key = os.urandom(32)
	logout_user()   
	flash("Logged out.")
	return redirect(url_for("login"))

@app.route("/gotosignup",methods=["GET"])
def gotosignup():
	return render_template("signup.html")

@app.route("/signup", methods=["GET","POST"])
def signup():
	if request.method=='POST' and request.form is not None:
		username=request.form["username"]
		email=request.form["email"]
		password=request.form["password"]
		u=insertUsers([username,email,password])
		if u!=0:
			session["userid"] = u.id
			session["username"]=u.username
			return render_template("projects.html",username=username)
		else:
			flash("Username/Email already exists. Please try a different one.")
			return render_template("signup.html")

@login_manager.user_loader
def load_user(id):
	return USERS.get(int(id))


@app.route("/reauth", methods=["GET", "POST"])
@login_required
def reauth():
	if request.method == "POST":
		confirm_login()
		flash(u"Reauthenticated.")
		return redirect(request.args.get("next") or url_for("login"))
	return render_template("reauth.html")

@app.route("/project")
def project():
	return render_template("project.html",orgname="Sample")

@app.route('/interview',methods=["POST","GET"])
def questionnaire():
		if "pid" in request.form and request.form["pid"]!="":
			pid=request.form["pid"]
			session["pid"]=pid
			p=Project.query.filter(Project.id==pid).first()
			params=[]
			params.append(p.orgname)
			params.append(p.name)
			params.append(p.prods)
			params.append(p.p_user)
			params.append(p.s_user)
			params.append(p.mission)
			params.append(p.sector)
			return render_template("project.html",params=params)
		else:
			try:
				userid=session["userid"]
				responses=[]
				return render_template("qanda.html",responses=responses)
			except KeyError:
				flash('Please login to access the page')
				return redirect(url_for('login'))

@app.route('/answer',methods=["POST","GET"])
def answer():
	return render_template("select_inds.html")

@app.route('/upload',methods=["POST","GET"])
def upload():
	if request.method == "POST" and request.form is not None:
		try:
			if request.form["update"]=="false":
				return render_template("indicators.html")
			orgname=request.form["orgname"]
			name=request.form["name"]
			pands=request.form["product"]
			client=request.form["client"]
			users=request.form["sec_client"]
			mission=request.form["mission"]
			sector=request.form["industry"]
			from models import Project, User
			userid=session["userid"]
			if(userid is not None): 
				p=Project(userid,orgname,name,sector,pands,client,users,mission)
				try:
					app.logger.debug("Adding project to the database")
					app.logger.debug(p)
					db_session.add(p)
					db_session.commit()
					app.logger.debug("Successfully added project to database")
				except Exception as e:
					app.logger.exception(e)
					flash("Project Name already exists. Please enter a different one")
				return render_template("indicators.html")
		except:
			app.logger.exception(traceback.format_exc())
	return redirect(url_for('questionnaire'))

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

@app.route('/showvars',methods=["POST","GET"])
def showvars():
	filename=""
	if request.method == "POST":
		try:
			file=request.files['varlist']
			if file and allowed_file(file.filename):
					app.logger.debug("Loading...")
					filename=secure_filename(file.filename)
					folder=app.config['UPLOAD_FOLDER']
					filepath=os.path.join(app.config['UPLOAD_FOLDER'], filename)
					app.logger.debug(filepath)
					file.save(filepath)
					userid=session["userid"]
					pid=session["pid"]
					Project.query.filter(Project.id==pid).update({"file_name":filename,"file_location":filepath})
					analysis=Analysis(pid)
					db_session.add(analysis)
					db_session.commit()
					return redirect(url_for("selectIndicators"))
		except:
			app.logger.exception(traceback.format_exc())
			return render_template("indicators.html",varfile=filename)

@app.route("/select_vars",methods=["GET","POST"])
def selectIndicators():
	if "vars" in session.keys() and session["vars"] is not None:
		vars=session["vars"]
	else:
		vars=[]
		pid=session["pid"]
		p=Project.query.filter(Project.id==pid).first()
		filename=p.file_name
		file_loc=p.file_location
		with open(str(file_loc),"rU") as csvfile:
			datareader=csv.reader(csvfile,delimiter=',')
			vars=datareader.next()
			session["vars"]=vars
			session["type"]="Input"
	return render_template("select_inds.html",vartype=session["type"],vars=vars)


@app.route("/store",methods=["POST","GET"])
def readinputs():
	if request.form is not None:
		inputs=request.form.getlist('variables')
		if(len(inputs)==0):
			flash("Please select at least one variable")
		else:
			userid=session["userid"]
			pid=session["pid"]
			a=Analysis.query.filter(Analysis.projid==pid).order_by(Analysis.id.desc()).first()
			try:  
				if session["type"]=="Input":
					for i in inputs:
					 io=Input(i,a.id)
					 db_session.add(io)
					db_session.commit() 
					session["type"]="Control"
				elif session["type"]=="Control":
					for i in inputs:
					  io=Control(i,a.id)
					  db_session.add(io)
					db_session.commit()      
					session["type"]="Output"
				else:
					for i in inputs:
					  io=Output(i,a.id)
					  db_session.add(io)
					db_session.commit()  
					return redirect(url_for("upload_data")) 
			except KeyError as e:
				app.logger.exception(e)
				session["type"]="Input"
			return redirect(url_for("selectIndicators"))  
				

@app.route("/upload_data")
def upload_data():
	return redirect(url_for("visualize"))

@app.route("/visualize")
def visualize():
	try:
		userid=session["userid"]
		pid=session["pid"]
		p=Project.query.filter(Project.id==pid).first()
		a=Analysis.query.filter(Analysis.projid==pid).order_by(Analysis.id.desc()).first()
		inputs=Input.query.filter(Input.analysis==a.id).all()
		outputs=Output.query.filter(Output.analysis==a.id).all()
		controls=Control.query.filter(Control.analysis==a.id).all()
		ivars=[i.varname for i in inputs if i.varname is not None]
		cvars=[c.varname for c in controls if c.varname is not None]
		ovars=[o.varname for o in outputs if o.varname is not None]
		filename=p.file_name
		file_loc=p.file_location
		csvf=convert.transform(file_loc)
		params=[]
		controls=[]
		count=0
		session['output']=[o for o in ovars]
		session['input']=[i for i in ivars]
		for c in cvars:
		 controls.append(c)
		for i in ivars: 
			for c in cvars:
				x=csvf[i].fillna(0)
				y=csvf[c].fillna(0)
				pltfile=analysis.scatter(x,y,count,i,c,config.ROOT_PATH)
				corr=np.corrcoef(x,y)[0][1]
				count+=1
				params.append((pltfile,corr))
		return render_template("scatter.html",params=params,vars=controls)
	except Exception as e:
		app.logger.exception(traceback.format_exc())
		flash('Sorry, an internal error occurred.')
		return redirect(url_for("logout"))
		'''
		To-do:
		Check if coefs>0.6
		Freeze values of coefficients 
		'''

@app.route("/regress",methods=["POST","GET"])
def regress():
	if request.method=="POST" and "variables" in request.form:
		variables=request.form.getlist('variables')
		pid=session["pid"]
		p=Project.query.filter(Project.id==pid).first()
		filename=p.file_name
		file_loc=p.file_location
		csvf=convert.transform(file_loc)
		reg=pd.DataFrame()
		out=session['output'][0]
		y=csvf[out]
		inp=session['input'][0]
		reg[inp]=csvf[inp].replace('nan',0)
		for var in variables:
			reg[var]=csvf[var].replace('nan',0)
		model=pd.ols(y=y,x=reg)
		output=sio.StringIO()
		output.write(model.summary)
		contents=output.getvalue()
		rpath='./static/files/regress.txt'
		f=open(rpath,'w+')
		f.write(contents)
		f.close()
		f=open(rpath,'r')
		lines=f.readlines()
		f.close()
		return render_template("regression.html",summary=lines)
	else:
		return redirect(url_for("logout"))

@app.errorhandler(500)
def internal_error(exception):
	app.logger.exception(exception)
	return render_template('500.html'),500

@app.errorhandler(404)
def internal_error(exception):
	app.logger.exception(exception)
	return render_template('500.html'),404

@app.teardown_appcontext
def shutdown_session(exception=None):
	db_session.remove()



if __name__=="__main__":
	app.run(host="localhost",port=8080)


