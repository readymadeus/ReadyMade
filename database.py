from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

username="jbqpsxeonpaptz"
password="O5lVxebs56qLeUTv9YotCU0Z3Z"
db="df2k3fqdn06r9c"
host="ec2-174-129-197-200.compute-1.amazonaws.com"
SQLALCHEMY_DATBASE_URI='postgresql://'+username+':'+password+'/'+db
# "postgresql+pg8000://scott:tiger@localhost/test"
engine = create_engine(SQLALCHEMY_DATBASE_URI, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import models
    Base.metadata.create_all(bind=engine)
    print Base.metadata.tables.keys()
    print Base.metadata.reflect(engine)

def insertUsers(values):
    from models import User
    try:
        print values
        u=User(str(values[0]),str(values[1]),str(values[2]))
        #u=User('use','emia','eere')
        print u
        db_session.add(u)
        db_session.commit()
        return 1
    except:
        return 0


def queryUser(username,password):
    from models import User
    print username,password
    user=User.query.filter(User.username==username,User.password==password)
    print "success"
    return user