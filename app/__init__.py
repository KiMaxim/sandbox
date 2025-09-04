from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate 
from flask_login import LoginManager
web_app = Flask(__name__)
web_app.config.from_object(Config)

db = SQLAlchemy(web_app)
Migre = Migrate(web_app, db)

login = LoginManager(web_app)
login.login_view = 'login' # type: ignore

from app import routes, models
