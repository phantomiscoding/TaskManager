from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from database import *

class User(db.Model, UserMixin):
    __tablename__ = 'users'  

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    
    tasks = db.relationship('Task', backref='user', lazy=True)

class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(250), nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  
