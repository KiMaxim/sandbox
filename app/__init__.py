from flask import Flask
from config import Config
web_app = Flask(__name__)
web_app.config.from_object(Config)
from app import routes
