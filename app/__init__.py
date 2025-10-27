import logging, os
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate 
from flask_login import LoginManager
from flask_mail import Mail

web_app = Flask(__name__)
web_app.config.from_object(Config)

db = SQLAlchemy(web_app)
Migre = Migrate(web_app, db)

login_manager = LoginManager(web_app)
login_manager.login_view = 'login' #type: ignore

mail = Mail(web_app)

if not web_app.debug:
    if web_app.config['MAIL_SERVER']:
        auth = None
        if web_app.config['MAIL_USERNAME'] and web_app.config['MAIL_PASSWORD']:
            auth = (web_app.config['MAIL_USERNAME'], web_app.config['MAIL_PASSWORD'])
        secure = None
        if web_app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(web_app.config['MAIL_SERVER'], web_app.config['MAIL_PORT']),
            fromaddr='no-reply@' + web_app.config['MAIL_SERVER'],
            toaddrs=web_app.config['ADMINS'], subject='Microblog Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        web_app.logger.addHandler(mail_handler)
    
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler('logs/sandbox.log', maxBytes=1024, backupCount=5)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    web_app.logger.addHandler(file_handler)

    web_app.logger.setLevel(logging.INFO)
    web_app.logger.info('Microblog startup')

from app import routes, models, errors
