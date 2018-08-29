#run to add users to DB

import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tabledef import *

engine = create_engine('sqlite:///tutorial.db', echo=True)
 
# create a Session
Session = sessionmaker(bind=engine)
session = Session()
 
# user = User("admin","password")
# session.add(user)
 
# user = User("python","python")
# session.add(user)
 
# user = User("jumpiness","python")
# session.add(user)
user = User("daliworks","dali123")
session.add(user)
user = User("kate","kate1234")
session.add(user)
user = User("kate_multitenancy","kate1234")
session.add(user)
# commit the record the database
session.commit()
 
session.commit()