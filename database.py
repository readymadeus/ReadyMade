from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

username="jbqpsxeonpaptz"
password="O5lVxebs56qLeUTv9YotCU0Z3Z"
db="df2k3fqdn06r9c"
host="ec2-174-129-197-200.compute-1.amazonaws.com"
SQLALCHEMY_DATBASE_URI='mysql://rm:rm@localhost/readymade'
engine = create_engine(SQLALCHEMY_DATBASE_URI, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    import models
    Base.metadata.create_all(bind=engine)
    print Base.metadata.tables.keys()
    print Base.metadata.reflect(engine)

def insertUsers(values):
    from models import User
    try: 
        u=User(str(values[0]),str(values[1]),str(values[2]))
        print u
        db_session.add(u)
        db_session.commit()
        return u
    except Exception as e:
        print e
        return 0


def queryUser(username,password):
    from models import User
    print username,password
    user=User.query.filter(User.username==username).filter(User.password==password)
    print "success"
    return user
