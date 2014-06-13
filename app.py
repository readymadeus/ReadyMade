import convert,analysis, csv, models, traceback, os, config, itertools,genpdf
from flask import Flask, request, render_template, redirect, url_for, flash, Blueprint,make_response
from flask.ext.login import (LoginManager, current_user, login_required,
							login_user, logout_user, UserMixin,
							confirm_login, fresh_login_required)
try:
	from flask.ext.login import AnonymousUser
except:
	from flask.ext.login import AnonymousUserMixin as AnonymousUser
from flask.ext.sqlalchemy import SQLAlchemy
from database import db_session, init_db, insertUsers, queryUser
from models import User
from werkzeug import secure_filename
import numpy as np
from models import User, Project, Input, Control, Output, Analysis
import pandas as pd
import sys

app=Flask(__name__)
data=dict()
session=dict()
UPLOAD_FOLDER=config.ROOT_PATH+'/static/files/uploads'
LOG_FILE=config.ROOT_PATH+'/app.log'
PLOTPATH=config.ROOT_PATH+"/static/images/plots"
REGRESS_PATH=config.ROOT_PATH+'/static/files/regressions/'
ALLOWED_EXTENSIONS=set(['csv'])
current_dir=os.getcwd()
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
app.config['PLOTPATH']=PLOTPATH
app.config['REGRESS_PATH']=REGRESS_PATH
username=""
session["plots"]=[]

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
	session.clear()
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
			print request.form
			pid=request.form["pid"]
			print "project id",pid
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
			print "Parameters to html",params
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

@app.route('/analyses',methods=["POST","GET"])
def analyses():
	pid=session["pid"]
	analyses=[]
	a=Analysis.query.filter_by(projid=pid).all()
	print "Analysis, ",a
	if a is not None:
		for each in a:
			if each.name is not None and each.report_loc is not None:
				report_loc=each.report_loc
				report_name=each.name+" on "+str(each.create_date)
				analyses.append((report_name,report_loc))
	return render_template("analysis.html",analyses=analyses)

@app.route('/saveproject',methods=["POST","GET"])
def saveproject():
	if request.method=="POST" and request.form is not None:
		try:
			if request.form["proj_status"]=="old":
				pid=session["pid"]
				print "Project id stored in session",session["pid"]
				'''from models import Project
				p=Project.query.filter_by(id=pid).first()'''
				if 'update' in request.form:
					udpates=request.form["update"]
					#TODO update flow
				return redirect(url_for('analyses'))
			else:
				orgname=request.form["orgname"]
				name=request.form["name"]
				pands=request.form["product"]
				client=request.form["client"]
				users=request.form["sec_client"]
				mission=request.form["mission"]
				sector=request.form["industry"]
				from models import Project
				userid=session["userid"]
				if userid is not None: 
					p=Project(userid,orgname,name,sector,pands,client,users,mission)
					try:
						app.logger.debug("Adding project to the database")
						app.logger.debug(p)
						db_session.add(p)
						db_session.commit()
						app.logger.debug("Successfully added project to database")
						session["pid"]=p.id
					except Exception as e:
						app.logger.exception(e)
						flash("Project Name already exists. Please enter a different one")
					return redirect(url_for('analyses'))
				else:
					flash("User ID missing. Please login again")
					return redirect(url_for('logout'))
		except:
			app.logger.exception(traceback.format_exc())

@app.route('/variables',methods=["POST","GET"])
def variables():
	if request.method=="POST" and request.form is not None:
		try:
			if 'vartype' in request.form:
				pid=session["pid"]
				print "Project id stored in session",session["pid"]
				from models import Project
				p=Project.query.filter_by(id=pid).first()
				orgname=p.orgname
				pands=p.prods
				if request.form["vartype"]=="input":
					aid=session["aid"]
					inputs=request.form.getlist("inputs")
					for inp in inputs:
						if len(inp)>0:
							io=Input("",inp,aid)
						 	db_session.add(io)
							db_session.commit() 
					return render_template("output_vars.html",orgname=orgname,pands=pands)
				elif request.form["vartype"]=="output":
					aid=session["aid"]
					outputs=request.form.getlist("outputs")
					for out in outputs:
						if len(out)>0:
							io=Output("",out,aid)
						 	db_session.add(io)
							db_session.commit() 
					return render_template("control_vars.html",orgname=orgname,pands=pands)
				else:
					a=Analysis(pid)
					db_session.add(a)
					db_session.commit()
					aid=a.id 
					session["aid"]=aid
					return render_template("input_vars.html",orgname=orgname,pands=pands)	
			else:
				from models import Project
				pid=session['pid']
				p=Project.query.filter_by(id=pid).first()
				orgname=p.orgname
				pands=p.prods
				a=Analysis(pid)
				db_session.add(a)
				db_session.commit()
				aid=a.id
				session["aid"]=aid
				return render_template("input_vars.html",orgname=orgname,pands=pands)
		except:
			app.logger.exception(traceback.format_exc())


@app.route('/upload',methods=["POST","GET"])
def upload():
	if request.method == "POST" and request.form is not None:
		try:
			pid=session["pid"]
			aid=session["aid"]
			controls=request.form.getlist("controls")			
			for c in controls:
				if len(c)>0:
					io=Control("",c,aid)
					db_session.add(io)
					db_session.commit()
			p=Project.query.filter_by(id=pid).first()
			filename=p.file_name
			if filename!=None:
				print filename
			else:
				filename=""
			return render_template("indicators.html",varfile=filename)
		except:
			app.logger.exception(traceback.format_exc())
	return redirect(url_for('questionnaire'))

def allowed_file(filename):
	return filename!='' and '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

@app.route('/showvars',methods=["POST","GET"])
def showvars():
	filename=""
	if request.method == "POST":
		try:
			file=request.files['varlist']
			print "File REceived",file
			if file and allowed_file(file.filename): 
					app.logger.debug("Loading...")
					filename=secure_filename(file.filename)
					folder=app.config['UPLOAD_FOLDER']
					filepath=os.path.join(app.config['UPLOAD_FOLDER'], filename)
					app.logger.debug(filepath)
					file.save(filepath)
					pid=session["pid"]
					Project.query.filter_by(id=pid).update({"file_name":filename,"file_location":filepath})
					db_session.commit()
					if "vars" in session.keys():
						session["vars"]=None
					return redirect(url_for("selectIndicators"))
			else:
				if "varfile" in request.form and allowed_file(request.form["varfile"]):
					app.logger.debug("Loading...")
					filename=request.form["varfile"]
					folder=app.config['UPLOAD_FOLDER']
					filepath=os.path.join(app.config['UPLOAD_FOLDER'], filename)
					app.logger.debug(filepath)
					pid=session["pid"]
					Project.query.filter_by(id=pid).update({"file_name":filename,"file_location":filepath})
					db_session.commit()
					if "vars" in session.keys():
						session["vars"]=None
					return redirect(url_for("selectIndicators"))
				else:
					flash("Please upload the data file")
					return render_template("indicators.html")
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
		p=Project.query.filter_by(id=pid).first()
		filename=p.file_name
		file_loc=p.file_location
		with open(str(file_loc),"rU") as csvfile:
			datareader=csv.reader(csvfile,delimiter=',')
			vars=datareader.next()
			print "Variable header ",vars
			session["vars"]=vars
			session["type"]="Input"
	uservars=getUserVars(session["type"])
	print "User variables for type  ",session["type"],"  are  ", 
	return render_template("select_inds.html",vartype=session["type"],vars=vars,uservars=uservars)

def getUserVars(vartype):
	aid=session["aid"]
	print "Analysis id is",aid
	uservars=[]
	if vartype=="Input":
		inps=Input.query.filter_by(analysis=aid).all()
		uservars=[inp.uservarname for inp in inps]
		return uservars
	elif vartype=="Output":
		outs=Output.query.filter_by(analysis=aid).all()
		uservars=[out.uservarname for out in outs]
		return uservars
	elif vartype=="Control":
		conts=Control.query.filter_by(analysis=aid).all()
		uservars=[cont.uservarname for cont in conts]
		return uservars
	else:
		return uservars

@app.route("/reselect_vars/<vartype>",methods=["GET","POST"])
def reselectIndicators(vartype):
	vars=session["vars"]
	uservars=getUserVars(vartype)
	print "User variables for type  ",session["type"],"  are  ",uservars
	return render_template("select_inds.html",vartype=vartype,vars=vars,uservars=uservars)

def getUserVars(vartype):
	aid=session["aid"]
	print "Analysis id is",aid
	uservars=[]
	if vartype=="Input":
		inps=Input.query.filter_by(analysis=aid).all()
		print inps
		uservars=[inp.uservarname for inp in inps]
		return uservars
	elif vartype=="Output":
		outs=Output.query.filter_by(analysis=aid).all()
		uservars=[out.uservarname for out in outs]
		return uservars
	elif vartype=="Control":
		conts=Control.query.filter_by(analysis=aid).all()
		uservars=[cont.uservarname for cont in conts]
		return uservars
	else:
		return uservars

@app.route("/store",methods=["POST","GET"])
def readinputs():
	if request.form is not None:
		uservars=request.form.keys()
		vardict={}
		for uvar in uservars:
			vardict[uvar]=request.form.getlist(uvar)
		if(len(vardict.values())==0):
			flash("Please select at least one variable")
			return redirect(url_for("selectIndicators"))
		else:
			userid=session["userid"]
			pid=session["pid"]
			aid=session["aid"]
			try:  
				if session["type"]=="Input":
					uvars=[uvar for uvar in uservars]
					for uvar,varnames in vardict.items():
						for varname in varnames:
							if varname!='nodata':
								io=Input(varname,uvar,aid)
								db_session.add(io)
					db_session.commit()
					session["type"]="Control"
				elif session["type"]=="Control":
					uvars=[uvar for uvar in uservars]
					for uvar,varnames in vardict.items():
						for varname in varnames:
							if varname!='nodata':
								io=Control(varname,uvar,aid)
								db_session.add(io)
					db_session.commit()
					session["type"]="Output"
				else:
					uvars=[uvar for uvar in uservars]
					for uvar,varnames in vardict.items():
						for varname in varnames:
							if varname!='nodata':
								io=Output(varname,uvar,aid)
								db_session.add(io)
					db_session.commit()
					return redirect(url_for("transform_data")) 
			except KeyError as e:
				app.logger.exception(e)
				session["type"]="Input"
			return redirect(url_for("selectIndicators"))  
				

@app.route("/transform_data")
def transform_data():
	pid=session["pid"]
	aid=session["aid"]
	p=Project.query.filter(Project.id==pid).first()
	inputs=Input.query.filter(Input.analysis==aid).all()
	controls=Control.query.filter(Control.analysis==aid).all()
	outputs=Output.query.filter(Output.analysis==aid).all()
	ovars=[o.varname for o in outputs if o.varname != None and o.varname!='']
	ivars=[i.varname for i in inputs if i.varname != None and i.varname!='']
	cvars=[c.varname for c in controls if c.varname != None and c.varname!='']
	filename=p.file_name
	file_loc=p.file_location
	csvf=convert.transform(file_loc)
	indices=[]
	var_out_info=[]
	for i in ivars:
		#Replace missing data
		try:
			csvf[i]=csvf[i].fillna(0)
			#Removing outliers
			outinfo=remOutliers(csvf[i])
			indices=outinfo[0]
			#csvf=csvf.drop(indices)
			var_out_info.append((i,outinfo[1],outinfo[2],outinfo[3]))
		except TypeError as e:
			app.logger.exception(traceback.format_exc())
			flash('Please select only numeric fields')
			
	#Output Variables
	for o in ovars:
		try:
			csvf[o]=csvf[o].fillna(0)
			#Removing outliers
			outinfo=remOutliers(csvf[o])
			indices=outinfo[0]
			#csvf=csvf.drop(indices)
			var_out_info.append((o,outinfo[1],outinfo[2],outinfo[3]))
		except TypeError as e:
			app.logger.exception(traceback.format_exc())
			flash('Please select only numeric fields')
	#session['var_out_info']=var_out_info
	session['output']=ovars
	session['input']=ivars
	session['control']=cvars
	data[pid]=csvf
	return render_template("outliers.html",data=var_out_info)

def remOutliers(data):
    outliers=data[abs(data-np.mean(data)) >=1.95*np.std(data)]
    indices=outliers.index
    removed=len(outliers)
    total=len(data)
    percent=(float(removed)/float(total))*100
    return (indices,removed,total,percent)
	

@app.route("/correlations",methods=["GET","POST"])
def correlations():
	if request.form is not None:
		'''ovars=session['output']
		ivars=session['input']
		lenvars=len(ovars)+len(ivars)
		if len(request.form.items())!=lenvars:
			flash("Please choose an option for all the variables.")
			return render_template("outliers.html",data=session["var_out_info"])'''
		pid=session["pid"]
		csvf=data[pid]
		for k,v in request.form.items():
			if v=='yes':
				indices=handleOutliers(csvf[k])
				mean=np.mean(csvf[k])
				for index in indices: 
					csvf.replace(to_replace=csvf[k][index],value=mean)
		ovars=session['output']
		ivars=session['input']
		cvars=session['control']
		if len(ovars)>1:
			return redirect(url_for("showcorr",vartype="output"))
		elif len(ivars)>1:
			session["rout"]=ovars
			return redirect(url_for("showcorr",vartype="input"))
		elif len(cvars)>1:
			session["rout"]=ovars
			session["rinp"]=ivars
			return redirect(url_for("showcorr",vartype="control"))
		else:
			session["rout"]=ovars
			session["rinp"]=ivars
			session["rcont"]=cvars
			return redirect(url_for("showcorr",vartype="regress"))
	else:
		return redirect(url_for("correlations"))


def handleOutliers(data):
	outliers=data[abs(data-np.mean(data)) >=1.95*np.std(data)]
	indices=outliers.index
	return indices

@app.route("/visualize/<vartype>",methods=["POST","GET"])
def showcorr(vartype=None):
	try:
		print "Session Dictionary",session
		vartype=str(vartype)
		if request.form is not None and "vartype" in request.form:
			vartype=request.form["vartype"]
		if vartype=="regress":
			if "rcont" not in session:
				session["rcont"]=list(set(request.form.getlist('variables')))
			return redirect(url_for("regress"))
		elif vartype=="output":
			corrvars=session['output']
		elif vartype=="input":
			if "rout" not in session:
				session["rout"]=list(set(request.form.getlist('variables')))
			corrvars=session["input"]
		else:
			if "rinp" not in session:
				session["rinp"]=list(set(request.form.getlist('variables')))
			corrvars=session["control"]
			ivars=session["input"]
		pid=session["pid"]
		csvf=data[pid]
		params=[]	
		nocor=[]
		cors=[]
		count=0
		plots=[]
		pltpath=app.config['PLOTPATH']+'/'+vartype+'/scatter'
		#Plotting the scatterplots
		i=0
		if vartype=="control":
			combos=itertools.combinations(corrvars+ivars,2)
		else:
			combos=itertools.combinations(corrvars,2)
		for combo in combos:
			#Redundancy removal for input variables in control correlations
			if vartype=="control" and combo[0] in ivars and combo[1] in ivars:
				continue
			x=csvf[combo[0]].fillna(0)
			#x=csvf[combo[0]].replace('',0)
			y=csvf[combo[1]].fillna(0)
			corr=np.corrcoef(x,y)[0][1]
			corr=round(corr,2)
			if corr>=0.70:
				pltfile=analysis.scatter(x,y,count,combo[0],combo[1],pltpath,vartype,corr)
				filepath='../static/images/plots/'+vartype+'/'+pltfile
				#Different path for accessing images through python files versus html files
				session["plots"].append(filepath[2:])
				count+=1
				params.append((filepath,corr,combo[0],combo[1]))
				cors.append(combo[0])
				cors.append(combo[1])
			else:
				session["plots"].append("")
				#create list of uncorrelated variables and pass it to vars
				if combo[0] not in ivars:
					nocor.append(combo[0])
				if combo[1] not in ivars:
					nocor.append(combo[1])
			cors=list(set(cors))
			nocor=list(set(nocor))
			nocor=[item for item in nocor if item not in cors]
		if count==0:
			msg="none"
		else:
			msg="corr"
		return render_template("scatter.html",params=params,vars=nocor,vartype=vartype,msg=msg)
	except Exception as e:
		app.logger.exception(traceback.format_exc())
		flash('Sorry, an internal error occurred.')


@app.route("/regress",methods=["POST","GET"])
def regress():
	if True:
		pid=session["pid"]
		regs=[]
		csvf=data[pid]
		reg=pd.DataFrame()
		outs=session['rout']
		inps=session['rinp']
		controls=session['rcont']
		count=0
		for o in outs:
			r=[]
			inputData=[]
			controlData=[]
			y=csvf[o]
			for i in inps:
				reg[i]=csvf[i]
			for control in controls:
				reg[control]=csvf[control]
			model=pd.ols(y=y,x=reg)
			formula="Measuring the impact of \""+', '.join(inps)+"\" on \""+o+"\" while controlling for variables such as \""+', '.join(controls)+"\""
			res=model.summary_as_matrix
			r.append(formula)
			r.append(round(model.r2_adj,2))
			r.append(round(model.f_stat['f-stat'],2))
			r.append(round(model.f_stat['p-value'],5))
			r.append(model.df)
			r.append(model.nobs)
			for i in inps:
				idata=[]
				idata.append(i)
				coef=round(res.ix['beta'][i],4)
				idata.append(coef)
				pval=round(res.ix['p-value'][i],4)
				idata.append(pval)
				stderr=round(res.ix['std err'][i],2)
				idata.append(stderr)
				tstat=round(res.ix['t-stat'][i],2)
				idata.append(tstat)
				inputData.append(idata)
			r.append(inputData)
			for c in controls:
				cdata=[]
				cdata.append(c)
				coef=round(res.ix['beta'][c],4)
				cdata.append(coef)
				pval=round(res.ix['p-value'][c],4)
				cdata.append(pval)
				stderr=round(res.ix['std err'][c],2)
				cdata.append(stderr)
				tstat=round(res.ix['t-stat'][c],2)
				cdata.append(tstat)
				controlData.append(cdata)
			r.append(controlData)
			regs.append(r)
			count+=1
			data["regs"]=regs
		return render_template("regression.html",regs=regs)
	else:
		return redirect(url_for("logout"))

@app.route("/report",methods=["GET","POST"])
def report():
	#Generate the PDF file
	plots=session["plots"]
	pdfplots=[]
	htmlplots=[]
	for plot in plots:
		pdfplots.append(config.ROOT_PATH+plot)
		htmlplots.append(".."+plot)
	from datetime import date
	today=date.today()
	pid=session["pid"]
	p=Project.query.filter_by(id=pid).first()
	pname=p.name
	orgname=p.orgname
	mission=p.mission
	product=p.prods
	puser=p.p_user
	inputs=','.join(session['rinp'])
	outputs=','.join(session['rout'])
	controls=','.join(session['rcont'])
	regs=data["regs"]
	pdfdata=[]
	pdfdata.append(str(today))
	pdfdata.append(pname)
	pdfdata.append(orgname)
	pdfdata.append(mission)
	pdfdata.append(product)
	pdfdata.append(puser)
	pdfdata.append(inputs)
	pdfdata.append(outputs)
	pdfdata.append(controls)
	pdfdata.append(pdfplots)
	pdfdata.append(regs)
	if config.ROOT_PATH=='.':
		pdfile='.'+genpdf.create_pdf(pdfdata)
	else:
		pdfile='..'+genpdf.create_pdf(pdfdata)
	pdfdata.append(pdfile)
	session['pdfile']=pdfile
	#Changing this part for the HTML page to access the images
	pdfdata[9]=htmlplots
	return render_template("report.html",data=pdfdata)

@app.route("/saving",methods=["POST"])
def saveanalysis():
	if request.form is not None:
		if "analysis" in request.form:
			aname=request.form["analysis"]
			aid=session["aid"]
			pdfile=session['pdfile']
			Analysis.query.filter_by(id=aid).update({"name":aname,"report_loc":pdfile})
			db_session.commit()
			return render_template("Thanks.html")
	
@app.route("/complete",methods=["GET","POST"])
def thanks():
	reportfile=UPLOAD_FOLDER+'/report.txt'
	return render_template("Thanks.html",filepath=reportfile)

@app.errorhandler(500)
def internal_error(exception):
	app.logger.exception(exception)
	return render_template('500.html'),500

@app.errorhandler(404)
def internal_error(exception):
	print exception
	app.logger.exception(exception)
	return render_template('500.html'),404

@app.teardown_appcontext
def shutdown_session(exception=None):
	db_session.remove()



if __name__=="__main__":
	app.run(host="localhost",port=8080)


