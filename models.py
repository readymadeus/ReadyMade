#Handle data and business logic
import datetime
from RMFlask import db


class Users(db.Document):
	userid=db.IntField(required=True)
	username=db.StringField(max_length=255,required=True)
	password=db.StringField(max_length=20)
	projects=db.ListField(db.EmbeddedDocumentField('Projects'))
	def get_username(self):
		return self.username

	def get_userid(self):
		return self.userid

	meta = {
		'allow_inheritance' : True,
		'indexes' : ['userid']
		}

class Projects(db.EmbeddedDocument):
	projid=db.IntField(required=True)
	userid=db.ReferenceField(Users)
	
	orgname=db.StringField(max_length=255)
	mission=db.StringField(max_length=1000)
	primary_user=db.StringField(max_length=255)
	secondary_user=db.StringField(max_length=255)
	other_users=db.ListField(db.StringField(max_length=255))
	input_vars=db.StringField(max_length=255)
	output_vars=db.StringField(max_length=255)
	control_vars=db.StringField(max_length=255)
	createdate=db.DateTimeField(default=datetime.datetime.now)
	updatedate=db.DateTimeField(default=datetime.datetime.now)

	def get_project_id(self):
		return self.projid
		
	def get_userid(self):
		return self.userid

	def get_orgname(self):
		return self.orgname

	def get_mission(self):
		return self.mission

	def get_primary_user(self):
		return self.primary_user

	def get_input_vars():
		return self.input_vars

	
