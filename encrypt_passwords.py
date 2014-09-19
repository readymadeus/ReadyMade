from database import db_session, init_db, insertUsers, queryUser
from models import User, Project, Input, Control, Output, Analysis
import hashlib


u=User.query.all()

for user in u:
	key_string = user.password
	salt = "1Ha7"
	password = salt+":"+hashlib.md5( salt + key_string).hexdigest()
	User.query.filter_by(id=user.id).update({"password":password})
db_session.commit()