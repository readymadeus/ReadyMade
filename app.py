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
UPLOAD_FOLDER='/Users/priyer/Box Sync/GSR/ReadyMade/RM/static/files/uploads'
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
login_manager.login_message = u"Please log in to access this page."
login_manager.refresh_view = "reauth"
login_manager.setup_app(app)

@app.route('/')
def hello():
    return render_template("rm_intro.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    print "login"
    if request.method == "POST" and "username" in request.form:
        username = str(request.form["username"])
        password = str(request.form["password"])
        project=[]
        userfound=False;
        from models import Project, User
        u=User.query.filter(User.username==username).filter(User.password==password).first()
        #u=db_session.query(q)
        #print u.id
        if u is not None:
            print "found"
            userfound=True
            '''resp=make_response(render_template("projects.html"))
            resp.set_cookie('userid',u.id)'''
            session['userid'] = u.id
            session['username']=u.username
        if userfound:
            remember = request.form.get("remember", "no") == "yes"
            projects=Project.query.filter(Project.userid==u.id).first()
            if projects is not None:
                project=projects
            else:
                project=[]
            return render_template("projects.html",username=u.username,projects=project)
        else:
            flash(u"Invalid username.")
    return render_template("rm_main.html")



@app.route('/interview',methods=["POST","GET"])
def questionnaire():
    responses=[]
    return render_template("qanda.html",responses=responses)

'''@app.route('/set_cookie/<cookie>&&<value>/')
def cookie_insertion(cookie,value):
    redirect_to_index = redirect('/')
    response = make_response(render_template("projects.html",username=username,projects=project))  
    response.set_cookie(cookie,value=value)
    return response'''

@app.route('/answer',methods=["POST","GET"])
def answer():
    return render_template("select_inds.html")

@app.route('/upload',methods=["POST","GET"])
def upload():
    if request.method == "POST" and request.form is not None:
        try:
            print request.form
            orgname=request.form["orgname"]
            pands=request.form["pands"]
            client=request.form["client"]
            users=request.form["users"]
            mission=request.form["mission"]
            sector=request.form["sector"]
            from models import Project, User
            #userid=request.cookies.get('userid')
            userid=session["userid"]
            print "userid",userid
            if(userid is not None):
                p=Project(userid,orgname,sector,pands,client,users,mission)
            #p=Project(userid=u.id,orgname=orgname,name="project1",p_user=client,prods=pands,sector=sector,s_user=users,mission=mission)
                print p
                db_session.add(p)
                db_session.commit()
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
                #file=request.form['varlist']
                if file and allowed_file(file.filename):
                    print "Loading..."
                    filename=secure_filename(file.filename)
                    folder=app.config['UPLOAD_FOLDER']
                    filepath=os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    #Save filename and file location in Projects
                    userid=session['userid']
                    Project.query.filter(Project.userid==userid).update({"file_name":filename,"file_location":filepath})
                    db_session.commit()
                    convert.csv_to_json(filename,folder)
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
        if session["type"]=="Input":
            session["type"]="Control"
        elif session["type"]=="Control":
            session["type"]="Output"
        else:
            print "type of session",session["type"]
            return redirect(url_for("visualize")) 
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
@login_required
def logout():
    session.pop('userid',None)
    session.pop('username',None)
    session.pop('vars',None)
    session.pop('type',None)
    session.clear()
    session["__invalidate__"] = True
    logout_user()
    flash("Logged out.")
    return redirect(url_for("login"))

@app.route("/gotosignup",methods=["GET"])
def gotosignup():
    return render_template("signup.html")

@app.route("/signup", methods=["GET","POST"])
def signup():
    print request.form
    if request.method=='POST' and request.form is not None:
        username=request.form["username"]
        email=request.form["email"]
        password=request.form["password"]
        status=insertUsers([username,email,password])
        if status==1:
            return render_template("projects.html",username=username)
        else:
            return render_template("signup.html")

@app.route("/store",methods=["POST","GET"])
def readinputs():
    print "request form in /store",request.form
    if request.form is not None:
        inputs=request.form.getlist('variables')
        print "inputs",inputs
        '''vars=session["vars"]
        vars=list(set(vars)-set(inputs))
        session["vars"]=vars'''
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
        #Set the type of variable being stored here
        return redirect(url_for("selectIndicators"))

@app.route("/visualize")
def visualize():
    userid=session["userid"]
    p=Project.query.filter(Project.userid==userid).first()
    inputs=Input.query.filter(Project.id==p.id).all()
    outputs=Output.query.filter(Project.id==p.id).all()
    controls=Control.query.filter(Project.id==p.id).all()
    ivars=[i.varname for i in inputs if i.varname is not None]
    cvars=[c.varname for c in controls if c.varname is not None]
    ovars=[o.varname for o in outputs if o.varname is not None]
    print ivars,cvars,ovars
    '''xvar=""
    yvar="loans_disbursed"
    return render_template("scatter.html",independent=xvar,dependent=yvar)'''

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__=="__main__":
    app.run(host="0.0.0.0", port=8080)

