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
import convert
from models import User, Project, Input, Control, Output 

app=Flask(__name__)
UPLOAD_FOLDER='./static/files/uploads'
ALLOWED_EXTENSIONS=set(['csv'])
current_dir=os.getcwd()
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
username=""

'''
app.config['SQLALCHEMY_DATBASE_URI']='mysql://rm:rm@localhost/readymade'
db=SQLAlchemy(app)
print db
'''
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
            session['userid'] = u.id
            session['username']=u.username
        if userfound:
            remember = request.form.get("remember", "no") == "yes"
            projects=Project.query.filter(Project.userid==u.id).all()
            if projects is not None:
                print projects
                projs=[]
                pids=[]
                for p in projects:
                    projs.append(p)
                    pids.append(p.id)
                session['pid']=pids
            else:
                pids=[]
                projs=[]    
            return render_template("projects.html",username=u.username,projects=projs)
        else:
            flash(u"Invalid username.")
    return render_template("rm_main.html")



@app.route('/interview',methods=["POST","GET"])
def questionnaire():
        if "pid" in request.form and request.form['pid']!="":
            pid=request.form['pid']
            session['pid']=pid
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
                userid=session['userid']
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
            print request.form
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
                    db_session.add(p)
                    db_session.commit()
                except Exception as e:
                    print e
                    flash("Project Name already exists. Please enter a different one")
                return render_template("indicators.html")
        except:
            print traceback.format_exc()
            

    return redirect(url_for('questionnaire'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

@app.route('/showvars',methods=["POST","GET"])
def showvars():
    filename=""
    if request.method == "POST":
        try:
            file=request.files['varlist']
            print file
            if True:
                if file and allowed_file(file.filename):
                    print "Loading..."
                    filename=secure_filename(file.filename)
                    folder=app.config['UPLOAD_FOLDER']
                    filepath=os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    print filepath
                    file.save(filepath)
                    userid=session['userid']
                    Project.query.filter(Project.userid==userid).update({"file_name":filename,"file_location":filepath})
                    db_session.commit()
                    convert.transform(filepath,folder)
                    return render_template("goto_inds.html",varfile=filename)
        except:
            print traceback.format_exc()
            

    return render_template("indicators.html",varfile=filename)

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

@app.route("/select_vars",methods=["GET","POST"])
def selectIndicators():
    if "vars" in session.keys() and session["vars"] is not None:
        vars=session["vars"]
    else:
        vars=[]
        userid=session["userid"]
        p=Project.query.filter(Project.userid==userid).first()
        filename=p.file_name
        file_loc=p.file_location
        with open(str(file_loc),"rU") as csvfile:
            datareader=csv.reader(csvfile,delimiter=',')
            vars=datareader.next()
            session["vars"]=vars
            session["type"]="Input"
    return render_template("select_inds.html",vartype=session["type"],vars=vars)

@app.route("/logout", methods=["GET", "POST"])
def logout():
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
            session['userid'] = u.id
            session['username']=u.username
            return render_template("projects.html",username=username)
        else:
            flash("Username/Email already exists. Please try a different one.")
            return render_template("signup.html")

@app.route("/store",methods=["POST","GET"])
def readinputs():
    print "request form in /store",request.form
    if request.form is not None:
        inputs=request.form.getlist('variables')
        if(len(inputs)==0):
            flash("Please select at least one variable")
        else:
            try:
                print "Variable type and variables"
                print session["type"],inputs
                if session["type"]=="Input":
                    session["type"]="Control"
                elif session["type"]=="Control":
                    session["type"]="Output"
                else:
                    print "type of session",session["type"]
                    return redirect(url_for("visualize")) 
            except KeyError:
                session["type"]="Input"
            userid=session["userid"]
            p=Project.query.filter(Project.userid==userid).first()
            for i in inputs:
                if session["type"]=="Input":
                    io=Input(i,p.id)
                elif session["type"]=="Control":
                    io=Control(i,p.id)
                else :
                    io=Output(i,p.id)
                db_session.add(io)
            db_session.commit()
        return redirect(url_for("selectIndicators"))

@app.route("/visualize")
def visualize():
    try:
        userid=session["userid"]
        p=Project.query.filter(Project.userid==userid).first()
        inputs=Input.query.filter(Project.id==p.id).all()
        print p.id
        outputs=Output.query.filter(Project.id==p.id).all()
        controls=Control.query.filter(Project.id==p.id).all()
        ivars=[i.varname for i in inputs if i.varname is not None]
        cvars=[c.varname for c in controls if c.varname is not None]
        ovars=[o.varname for o in outputs if o.varname is not None]
        print ivars,cvars,ovars
        params=[ivars,cvars,ovars]
        return render_template("scatter.html",params=params)
    except Exception as e:
        print e
        return redirect(url_for("login"))

@app.route("/project")
def project():
    return render_template("project.html",orgname="Sample")

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__=="__main__":
    app.debug=True
    app.run(host="0.0.0.0",port=8080)


