from app import web_app, db
import sqlalchemy as sqla
import sqlalchemy.orm as orm
from app.models import User, Post

@web_app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'sqla': sqla, 'orm': orm}
