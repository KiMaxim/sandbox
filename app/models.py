from typing import Optional 
from flask_login import UserMixin
import sqlalchemy as sqla
import sqlalchemy.orm as orm
from app import db, login
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash

@login.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

class User(db.Model, UserMixin):

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    login: orm.Mapped[str] = orm.mapped_column(sqla.String(64), unique=True, index=True)
    email: orm.Mapped[str] = orm.mapped_column(sqla.String(120), unique=True, index=True)
    password_hash: orm.Mapped[Optional[str]] = orm.mapped_column(sqla.String(128))

    posts: orm.WriteOnlyMapped['Post'] = orm.relationship('Post', back_populates='author', lazy='dynamic')

    def __repr__(self) -> str:
        return f"User {self.login}"
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256') #adding method in shell too, so it works correctly

    def check_password(self, password):
        if self.password_hash is None: # in case password is not set
            return False
        return check_password_hash(self.password_hash, password)
        
    
class Post(db.Model):
    post_id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    body: orm.Mapped[str] = orm.mapped_column(sqla.String(140))
    timestamp: orm.Mapped[Optional[str]] = orm.mapped_column(sqla.DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    user_id: orm.Mapped[int] = orm.mapped_column(sqla.ForeignKey(User.id), index=True)

    author: orm.Mapped[User] = orm.relationship(back_populates='posts')

    def __repr__(self) -> str:
        return f"Post {self.body}"
