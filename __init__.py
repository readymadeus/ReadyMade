from flask import Flask
from flask.ext.mongoengine import MongoEngine

app=Flask(__name__)
app.config["MONGODB_SETTINGS"]={'DB':"rmdb"}
#app.config["SECRET_KEY"]="ReadyMade4Lyfe"

db=MongoEngine(app)

#Registering the blueprint
def register_blueprints(app):
    # Prevents circular imports
    from RMFlask.views import projects
    app.register_blueprint(projects)

register_blueprints(app)

@app.route('/')
def hello():
	return "Hello World!"



if __name__=='__main__':
	app.run()

