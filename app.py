import convert,analysis, csv, models, traceback, os, config, itertools,genpdf
from flask import Flask, request, render_template, redirect, url_for, flash, Blueprint,make_response,session
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
import hashlib
import uuid



'''
when user logs in:
check whether cookie has session id
if yes, store that session id 
if not, create a new session id and store in cookie
use that session id as index of dictionary to store variables
@app.route('/set_cookie')
def cookie_insertion():
    redirect_to_index = redirect('/index')
    response = current_app.make_response(redirect_to_index )  
    response.set_cookie('cookie_name',value='values')
    return response


when user logs out:
clear session cache

'''


app=Flask(__name__)
data=dict()
sessions=[]
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
    #session['uid']=uuid.uuid4()
    app.secret_key = os.urandom(32)
    logout_user()   
    if request.method == "POST" and "username" in request.form:
        username = str(request.form["username"])
        key_string = str(request.form["password"])
        salt = "1Ha7"
        password = salt+":"+hashlib.md5( salt + key_string).hexdigest()
        userfound=False
        from models import User
        u=User.query.filter(User.username==username).filter(User.password==password).first()
        if u is not None:
            userfound=True
            sessionid=session['_id']
            session['id']=sessionid
            print "session id",session
            '''
            For production,
            sessionid is uuid.
            '''
            data[sessionid]=dict()
            data[sessionid]["username"]=u.username
            data[sessionid]["userid"]=u.id
            '''session["userid"] = u.id
            session["username"]=u.username'''
        if userfound:
            #session["userid"] = u.id
            remember = request.form.get("remember", "no") == "yes"
            return redirect(url_for('cookie_insertion'))
        else:
            flash("Invalid username")
    return render_template("rm_main.html")

@app.route('/set_cookie')
def cookie_insertion():
    sessionid=session['id']
    username=data[sessionid]["username"]
    print username, sessionid
    redirect_to_projects = redirect(url_for("showprojects"))
    response = app.make_response(redirect_to_projects)  
    response.set_cookie(sessionid,username)
    return response

@app.route("/logout", methods=["GET", "POST"])
def logout():
    sessionid=session['id']
    redirect_to_login=redirect(url_for("login"))
    response=app.make_response(redirect_to_login)
    print request.cookies
    response.set_cookie(sessionid, '', expires=0)
    app.secret_key = os.urandom(32)
    logout_user()   
    flash("Logged out.")
    session.clear()
    return response

@app.route("/gotosignup",methods=["GET"])
def gotosignup():
    return render_template("signup.html")

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method=='POST' and request.form is not None:
        username=request.form["username"]
        email=request.form["email"]
        key_string = str(request.form["password"])
        salt = "1Ha7"
        password = salt+":"+hashlib.md5( salt + key_string).hexdigest()
        u=insertUsers([username,email,password])
        if u!=0:
            '''session["userid"] = u.id
            session["username"]=u.username'''
            sessionid=session['id']
            data[sessionid]=dict()
            data[sessionid]["username"]=u.username
            data[sessionid]["userid"]=u.id
            return redirect(url_for('cookie_insertion'))
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

@app.route("/projects")
def showprojects():
    from models import Project
    sessionid=session['id']
    uid=data[sessionid]["userid"]
    username=data[sessionid]["username"]
    projects=Project.query.filter(Project.userid==uid).all()
    if projects is not None:
        print "Projects Page"
        projs=[]
        pids=[]
        for p in projects:
            projs.append(p)
            pids.append(p.id)
    else:
        pids=[]
        projs=[]    

    return render_template("projects.html",username=username,projects=projs)


@app.route("/project")
def project():
    return render_template("project.html",orgname="Sample")

@app.route('/interview',methods=["POST","GET"])
def questionnaire():
        sessionid=session['id']
        if "pid" in request.form and request.form["pid"]!="":
            print request.form
            pid=request.form["pid"]
            print "project id",pid
            data[sessionid]["pid"]=pid
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
                userid=data[sessionid]["userid"]
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
    sessionid=session['id']
    pid=data[sessionid]["pid"]
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
        sessionid=session['id']
        try:
            if request.form["proj_status"]=="old":
                pid=data[sessionid]["pid"]
                print "Project id stored in data[sessionid]",data[sessionid]["pid"]
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
                print data
                userid=data[sessionid]["userid"]
                if userid is not None: 
                    p=Project(userid,orgname,name,sector,pands,client,users,mission)
                    try:
                        app.logger.debug("Adding project to the database")
                        app.logger.debug(p)
                        db_session.add(p)
                        db_session.commit()
                        app.logger.debug("Successfully added project to database")
                        data[sessionid]["pid"]=p.id
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
        sessionid=session['id']
        try:
            if 'vartype' in request.form:
                pid=data[sessionid]["pid"]
                print "Project id stored in data[sessionid]",data[sessionid]["pid"]
                from models import Project
                p=Project.query.filter_by(id=pid).first()
                orgname=p.orgname
                pands=p.prods
                if request.form["vartype"]=="output":
                    aid=data[sessionid]["aid"]
                    outputs=request.form.getlist("outputs")
                    for out in outputs:
                        if len(out)>0:
                            io=Output("",out,aid)
                            db_session.add(io)
                            db_session.commit() 
                    return render_template("input_vars.html",orgname=orgname,pands=pands)
                elif request.form["vartype"]=="input":
                    aid=data[sessionid]["aid"]
                    inputs=request.form.getlist("inputs")
                    for inp in inputs:
                        if len(inp)>0:
                            io=Input("",inp,aid)
                            db_session.add(io)
                            db_session.commit() 
                    return render_template("control_vars.html",orgname=orgname,pands=pands)
                else:
                    a=Analysis(pid)
                    db_session.add(a)
                    db_session.commit()
                    aid=a.id 
                    data[sessionid]["aid"]=aid
                    return render_template("output_vars.html",orgname=orgname,pands=pands)  
            else:
                from models import Project
                pid=data[sessionid]['pid']
                p=Project.query.filter_by(id=pid).first()
                orgname=p.orgname
                pands=p.prods
                a=Analysis(pid)
                db_session.add(a)
                db_session.commit()
                aid=a.id
                data[sessionid]["aid"]=aid
                return render_template("output_vars.html",orgname=orgname,pands=pands)
        except:
            app.logger.exception(traceback.format_exc())


@app.route('/upload',methods=["POST","GET"])
def upload():
    if request.method == "POST" and request.form is not None:
        sessionid=session['id']
        try:
            pid=data[sessionid]["pid"]
            aid=data[sessionid]["aid"]
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
    sessionid=session['id']
    data[sessionid]["plots"]=[]
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
                    pid=data[sessionid]["pid"]
                    Project.query.filter_by(id=pid).update({"file_name":filename,"file_location":filepath})
                    db_session.commit()
                    if "vars" in data[sessionid].keys():
                        data[sessionid]["vars"]=None
                    return redirect(url_for("selectIndicators"))
            else:
                if "varfile" in request.form and allowed_file(request.form["varfile"]):
                    app.logger.debug("Loading...")
                    filename=request.form["varfile"]
                    folder=app.config['UPLOAD_FOLDER']
                    filepath=os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    app.logger.debug(filepath)
                    pid=data[sessionid]["pid"]
                    Project.query.filter_by(id=pid).update({"file_name":filename,"file_location":filepath})
                    db_session.commit()
                    if "vars" in data[sessionid].keys():
                        data[sessionid]["vars"]=None
                    return redirect(url_for("selectIndicators"))
                else:
                    flash("Please upload the data file in the correct format")
                    return render_template("indicators.html")
        except:
            app.logger.exception(traceback.format_exc())
            return render_template("indicators.html",varfile=filename)

@app.route("/select_vars",methods=["GET","POST"])
def selectIndicators():
    sessionid=session['id']
    if "vars" in data[sessionid].keys() and data[sessionid]["vars"] is not None:
        vars=data[sessionid]["vars"]
    else:
        vars=[]
        pid=data[sessionid]["pid"]
        p=Project.query.filter_by(id=pid).first()
        filename=p.file_name
        file_loc=p.file_location
        csvf = pd.read_csv(file_loc)
        non_numeric_vars = []
        for col in csvf.columns:
            col_dtype = csvf[col].dtype
            if not (col_dtype in (np.float64, np.int64)):
                print col + " non-numeric and rejected."
                non_numeric_vars.append(col)
                del csvf[col]
        vars = csvf.columns.values.tolist()
        print vars
        print non_numeric_vars
        data[sessionid]["vars"]=vars
        data[sessionid]["vars_rejected"]=non_numeric_vars
        data[sessionid]["type"]="Output"
    uservars=getUserVars(data[sessionid]["type"])
    print "User variables for type  ",data[sessionid]["type"],"  are  ", 
    return render_template("select_inds.html",vartype=data[sessionid]["type"],vars=vars,uservars=uservars)

def getUserVars(vartype):
    sessionid=session['id']
    aid=data[sessionid]["aid"]
    print "Analysis id is",aid
    uservars=[]
    if vartype=="Output":
        outs=Output.query.filter_by(analysis=aid).all()
        uservars=[out.uservarname for out in outs]
        return uservars
    elif vartype=="Input":
        inps=Input.query.filter_by(analysis=aid).all()
        uservars=[inp.uservarname for inp in inps]
        return uservars
    elif vartype=="Control":
        conts=Control.query.filter_by(analysis=aid).all()
        uservars=[cont.uservarname for cont in conts]
        return uservars
    else:
        return uservars

@app.route("/reselect_vars/<vartype>",methods=["GET","POST"])
def reselectIndicators(vartype):
    sessionid=session['id']
    vars=data[sessionid]["vars"]
    uservars=getUserVars(vartype)
    print "User variables for type  ",data[sessionid]["type"],"  are  ",uservars
    return render_template("select_inds.html",vartype=vartype,vars=vars,uservars=uservars)

def getUserVars(vartype):
    sessionid=session['id']
    aid=data[sessionid]["aid"]
    print "Analysis id is",aid
    uservars=[]
    if vartype=="Output":
        outs=Output.query.filter_by(analysis=aid).all()
        uservars=[out.uservarname for out in outs]
        return uservars
    elif vartype=="Input":
        inps=Input.query.filter_by(analysis=aid).all()
        print inps
        uservars=[inp.uservarname for inp in inps]
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
        sessionid=session['id']
        uservars=request.form.keys()
        vardict={}
        for uvar in uservars:
            vardict[uvar]=request.form.getlist(uvar)
        if(len(vardict.values())==0):
            flash("Please select at least one variable")
            return redirect(url_for("selectIndicators"))
        else:
            userid=data[sessionid]["userid"]
            pid=data[sessionid]["pid"]
            aid=data[sessionid]["aid"]
            try:  
                if data[sessionid]["type"]=="Output":
                    uvars=[uvar for uvar in uservars]
                    for uvar,varnames in vardict.items():
                        for varname in varnames:
                            if varname!='nodata':
                                io=Output(varname,uvar,aid)
                                db_session.add(io)
                    db_session.commit()
                    #session["type"]="Control"
                    data[sessionid]["type"]="Input"
                #elif session["type"]=="Control":
                elif data[sessionid]["type"]=="Input":
                    uvars=[uvar for uvar in uservars]
                    for uvar,varnames in vardict.items():
                        for varname in varnames:
                            if varname!='nodata':
                                #io=Control(varname,uvar,aid)
                                io=Input(varname,uvar,aid)
                                db_session.add(io)
                    db_session.commit()
                    #session["type"]="Output"
                    data[sessionid]["type"]="Control"
                else:
                    uvars=[uvar for uvar in uservars]
                    for uvar,varnames in vardict.items():
                        for varname in varnames:
                            if varname!='nodata':
                                #io=Output(varname,uvar,aid)
                                io=Control(varname,uvar,aid)
                                db_session.add(io)
                    db_session.commit()
                    return redirect(url_for("transform_data")) 
            except KeyError as e:
                app.logger.exception(e)
                data[sessionid]["type"]="Output"
            return redirect(url_for("selectIndicators"))  
                

@app.route("/transform_data")
def transform_data():
    sessionid=session['id']
    pid=data[sessionid]["pid"]
    aid=data[sessionid]["aid"]
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
    data[sessionid]['output']=ovars
    data[sessionid]['input']=ivars
    data[sessionid]['control']=cvars
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
        sessionid=session['id']
        pid=data[sessionid]["pid"]
        csvf=data[pid]
        for k,v in request.form.items():
            if v=="yes":
                indices=handleOutliers(csvf[k])
                mean=np.mean(csvf[k])
                for index in indices: 
                    csvf=csvf.replace(to_replace=csvf[k][index],value=mean)#replacing outliers with the mean
                print indices, len(indices)
        ovars=data[sessionid]['output']
        ivars=data[sessionid]['input']
        cvars=data[sessionid]['control']
        if len(ovars)>1:
            return redirect(url_for("showcorr",vartype="output"))
        elif len(ivars)>1:
            data[sessionid]["rout"]=ovars
            return redirect(url_for("showcorr",vartype="input"))
        elif len(cvars)>1:
            data[sessionid]["rout"]=ovars
            data[sessionid]["rinp"]=ivars
            return redirect(url_for("showcorr",vartype="control"))
        else:
            data[sessionid]["rout"]=ovars
            data[sessionid]["rinp"]=ivars
            data[sessionid]["rcont"]=cvars
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
        sessionid=session['id']
        print "data[sessionid] Dictionary",data[sessionid]
        vartype=str(vartype)
        if request.form is not None and "vartype" in request.form:
            vartype=request.form["vartype"]
        if vartype=="regress":
            if "rcont" not in data[sessionid]:
                data[sessionid]["rcont"]=list(set(request.form.getlist('variables')))
            return redirect(url_for("regress"))
        elif vartype=="output":
            corrvars=data[sessionid]['output']
        elif vartype=="input":
            if "rout" not in data[sessionid]:
                data[sessionid]["rout"]=list(set(request.form.getlist('variables')))
            corrvars=data[sessionid]["input"]
        else:
            if "rinp" not in data[sessionid]:
                data[sessionid]["rinp"]=list(set(request.form.getlist('variables')))
            corrvars=data[sessionid]["control"]
            ivars=data[sessionid]["input"]
        pid=data[sessionid]["pid"]
        csvf=data[pid]
        params=[]   
        nocor=[]
        cors=[]
        vars=[]
        count=0
        plots=[]
        pltpath=app.config['PLOTPATH']+'/'+vartype+'/scatter'
        #Plotting the scatterplots
        i=0
        skipPlot=False
        if vartype=="control":
            combos=itertools.combinations(corrvars+ivars,2)
        else:
            if len(corrvars)==1:
                skipPlot=True;
            else:
                combos=itertools.combinations(corrvars,2)
            
        if skipPlot is False:   
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
                    data[sessionid]["plots"].append(filepath[2:])
                    count+=1
                    #params.append((filepath,corr,combo[0],combo[1]))
                    params.append((filepath,corr))
                    cors.append(combo[0])
                    cors.append(combo[1])
                else:
                    #create list of uncorrelated variables and pass it to vars
                    if vartype=="control":
                        if combo[0] not in ivars:
                            nocor.append(combo[0])
                        if combo[1] not in ivars:
                            nocor.append(combo[1])
                    else:
                        nocor.append(combo[0])
                        nocor.append(combo[1])
            cors=list(set(cors))
            nocor=list(set(nocor))
            nocor=[item for item in nocor if item not in cors]
            vars.append(cors)
            vars.append(nocor)
            if count==0:
                msg="none"
            else:
                msg="corr"
            if len(params)>3:
                height=str(int(len(params)/3)*500)+"px"
            else:
                height="500px"
            return render_template("scatter.html",params=params,vars=vars,vartype=vartype,msg=msg,height=height)
        else:
            if vartype=="output":
                data[sessionid]["rout"]=data[sessionid]["output"]
                vartype="input"
            elif vartype=="input":
                data[sessionid]["rinp"]=data[sessionid]["input"]
                vartype="control"
            elif vartype=="control":
                data[sessionid]["rcont"]=data[sessionid]["control"]
                vartype=="regress"
            else: 
                return redirect(url_for("regress"))
            return redirect(url_for("showcorr",vartype=vartype))
    except Exception as e:
        app.logger.exception(traceback.format_exc())
        flash('Sorry, an internal error occurred.')


@app.route("/regress",methods=["POST","GET"])
def regress():
    if True:
        sessionid=session['id']
        pid=data[sessionid]["pid"]
        regs=[]
        csvf=data[pid]
        reg=pd.DataFrame()
        outs=data[sessionid]['rout']
        inps=data[sessionid]['rinp']
        controls=data[sessionid]['rcont']
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
            r.append(o)
            regs.append(r)
            count+=1
            data["regs"]=regs
        return render_template("regression.html",regs=regs)
    else:
        return redirect(url_for("logout"))

@app.route("/report",methods=["GET","POST"])
def report():
    #Generate the PDF file
    sessionid=session['id']
    plots=data[sessionid]["plots"]
    pdfplots=[]
    htmlplots=[]
    for plot in plots:
        pdfplots.append(config.ROOT_PATH+plot)
        htmlplots.append(".."+plot)
    from datetime import date
    today=date.today()
    pid=data[sessionid]["pid"]
    p=Project.query.filter_by(id=pid).first()
    pname=p.name
    orgname=p.orgname
    mission=p.mission
    product=p.prods
    puser=p.p_user
    inputs=','.join(data[sessionid]['rinp'])
    outputs=','.join(data[sessionid]['rout'])
    controls=','.join(data[sessionid]['rcont'])
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
    data[sessionid]['pdfile']=pdfile
    #Changing this part for the HTML page to access the images
    pdfdata[9]=htmlplots
    return render_template("report.html",data=pdfdata)

@app.route("/saving",methods=["POST"])
def saveanalysis():
    if request.form is not None:
        sessionid=session['id']
        if "analysis" in request.form:
            aname=request.form["analysis"]
            aid=data[sessionid]["aid"]
            pdfile=data[sessionid]['pdfile']
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


