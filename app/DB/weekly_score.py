from sqlalchemy.orm import sessionmaker,DeclarativeBase
from sqlalchemy import Column, Integer, String, create_engine

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from models import PlayerSeasonHistory, Participants

#CONNECT TO DATABASE
API_DATABASE_URI = "mysql+pymysql://root:new_password@localhost:3306/apis"
#or use a url object with #URL

db = SQLAlchemy()
app= Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = API_DATABASE_URI
db.init_app(app)

engine = create_engine(API_DATABASE_URI) 
connection = engine.connect()

with app.app_context():
    db.create_all()
    print(db.session())

#tried to figure out reflection
#and also confirming actions from python work in db
#working with 2 models now, PlayerSeasonHistory ..

#https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/api/#flask_sqlalchemy.SQLAlchemy.create_all

#class Participant:
    #__table__ = db.metadatas["auth"].tables["participants"]

#connection.commit()
#connection.close()
print("Done")



