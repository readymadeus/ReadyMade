from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref
from database import Base
from datetime import datetime

#Base = declarative_base()
class User(Base):
	__tablename__ = 'User'
	id=Column(Integer,primary_key=True)
	username=Column(String(80),unique=True)
	email=Column(String(120),unique=True)
	password=Column(String(120))
	projects=relationship('Project')

	def __init__(self,username,email,password):
		self.username=username
		self.email=email
		self.password=password

	def __repr__(self):
		return '<User %r,%r,%r>' %(self.id,self.username,self.password)


class Project(Base):
	__tablename__ = 'Project'
	id=Column(Integer,primary_key=True)
	userid=Column(Integer,ForeignKey('User.id'))
	orgname=Column(String(100))
	name=Column(String(100),unique=True)
	mission=Column(String(100))
	p_user=Column(String(100))
	s_user=Column(String(100))
	sector=Column(String(100))
	prods=Column(String(100))
	other_user=Column(String(100))
	file_name=Column(String(100))
	file_location=Column(String(100))
	analysis=relationship('Analysis')


	def __init__(self,userid,orgname,name,sector,prods,p_user,s_user,mission):
		self.userid=userid
		self.sector=sector
		self.orgname=orgname
		self.name=name
		self.sector=sector
		self.prods=prods
		self.p_user=p_user
		self.s_user=s_user
		self.mission=mission

	def __repr__(self):
		return '<Project %r,%r,%r,%r,%r,%r,%r,%r,%r,%r>' %(self.id,self.orgname,self.name,self.sector,self.prods,self.p_user,self.s_user,self.mission,self.file_name,self.file_location)

class Analysis(Base):
	__tablename__ = 'Analysis'
	id=Column(Integer,primary_key=True)
	projid=Column(Integer,ForeignKey('Project.id'))
	report_loc=Column(String(200))
	name=Column(String(200))
	create_date=Column(DateTime,default=datetime.now)
	inputs=relationship('Input')
	outputs=relationship('Output')
	controls=relationship('Control')
	stats=relationship('Statistics')

	def __init__(self,projid):
		self.projid=projid

	def __repr__(self):
		return '<Analysis %r,%r,%r,%r>' %(self.id,self.name,self.create_date,self.report_loc)

class Input(Base):
	__tablename__ = 'Inputs'
	id=Column(Integer,primary_key=True)
	varname=Column(String(500))
	uservarname=Column(String(500))
	analysis=Column(Integer,ForeignKey('Analysis.id'))

	def __init__(self,varname,uservarname,analysis):
		self.varname=varname
		self.analysis=analysis
		self.uservarname=uservarname

	def __repr__(self):
		return '<Input %r>' %self.varname

class Output(Base):
	__tablename__ = 'Outputs'
	id=Column(Integer,primary_key=True)
	varname=Column(String(500))
	uservarname=Column(String(500))
	analysis=Column(Integer,ForeignKey('Analysis.id'))

	def __init__(self,varname,uservarname,analysis):
		self.varname=varname
		self.analysis=analysis
		self.uservarname=uservarname

	def __repr__(self):
		return '<Output %r>' %self.varname

class Control(Base):
	__tablename__ = 'Controls'
	id=Column(Integer,primary_key=True)
	varname=Column(String(500))
	uservarname=Column(String(500))
	analysis=Column(Integer,ForeignKey('Analysis.id'))

	def __init__(self,varname,uservarname,analysis):
		self.varname=varname
		self.analysis=analysis
		self.uservarname=uservarname

	def __repr__(self):
		return '<Controls %r>' %self.varname
	

class Statistics(Base):
	__tablename__ = 'Statistics'
	id=Column(Integer,primary_key=True)
	analysis=Column(Integer,ForeignKey('Analysis.id'))
	stat=Column(String(50))
	input=Column(String(100))
	measure=Column(Integer)

	def __init__(self,analysis,stat,measure):
		self.analysis=analysis
		self.measure=measure
		self.stat=stat

	def __repr__(self):
		return '<Statistics %r>' %self.stat
