from datetime import datetime

from flask import Flask, appcontext_pushed
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__) 
app.config['SECRET_KEY'] = 'be321770c3b21079279c41eb1de1ee69'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from mens_fashion import route
