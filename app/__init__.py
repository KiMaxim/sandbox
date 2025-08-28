from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate 
web_app = Flask(__name__)
web_app.config.from_object(Config)
db = SQLAlchemy(web_app)
Migre = Migrate(web_app, db)
from app import routes
