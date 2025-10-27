import sqlalchemy.orm as orm
import sqlalchemy as sqla
import jwt
from typing import Optional 
from flask_login import UserMixin
from app import db, login_manager, web_app
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
from dataclasses import dataclass
from time import time

'''
responsible for managin whether the user is already in the system or not. 
if the user is logged in, load the corresponding data
'''

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

follower = sqla.Table(
    'followers',
    db.metadata,
    sqla.Column('follower_id', sqla.Integer, sqla.ForeignKey('user.id')),
    sqla.Column('followed_id', sqla.Integer, sqla.ForeignKey('user.id'))
)

@dataclass
class User(db.Model, UserMixin):

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    login: orm.Mapped[str] = orm.mapped_column(sqla.String(64), unique=True, index=True)
    email: orm.Mapped[str] = orm.mapped_column(sqla.String(120), unique=True, index=True)
    password_hash: orm.Mapped[str] = orm.mapped_column(sqla.String(128))
    about_me: orm.Mapped[Optional[str]] = orm.mapped_column(sqla.String(1256))
    last_seen: orm.Mapped[Optional[datetime]] = orm.mapped_column(default=lambda: datetime.now(timezone.utc))

    following: orm.WriteOnlyMapped['User'] = orm.relationship(
        secondary=follower, 
        primaryjoin=(follower.c.follower_id == id),
        secondaryjoin=(follower.c.followed_id == id),
        back_populates='followers'
    )

    followers: orm.WriteOnlyMapped['User'] = orm.relationship(
        secondary=follower, 
        primaryjoin=(follower.c.followed_id == id),
        secondaryjoin=(follower.c.follower_id == id),
        back_populates='following'
    )

    posts: orm.WriteOnlyMapped['Post'] = orm.relationship('Post', back_populates='author', lazy='dynamic')

    def __repr__(self) -> str:
        return f"User {self.login}"
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256') #adding method in shell too, so it works correctly

    def check_password(self, password):
        if self.password_hash is None: # in case password is not set
            return False
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f"https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}"
    
    def follow(self, user):
        if not self.is_following(user):
            self.following.add(user)

    def is_following(self, user):
        query = self.following.select().where(User.id == user.id)
        return db.session.scalar(query) is not None
    
    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)
    
    def followers_count(self):
        query = sqla.select(sqla.func.count()).select_from(self.followers.select().subquery())
        return db.session.scalar(query)
    
    def following_count(self):
        query = sqla.select(sqla.func.count()).select_from(self.following.select().subquery())
        return db.session.scalar(query)

    def following_posts(self):
        Author = orm.aliased(User)
        Follower = orm.aliased(User)
        return (
            sqla.select(Post)
            .join(Post.author.of_type(Author))
            .join(Author.followers.of_type(Follower), isouter=True)
            .where(sqla.or_(
                    Follower.id == self.id,
                    Author.id == self.id,
                ))
            .group_by(Post.post_id)
            .order_by(Post.timestamp.desc())
        )
    
    def get_reset_password_token(self, expiresIn=600):
        return jwt.encode({'user_id': self.id, 'exp': time() + expiresIn}, web_app.config['SECRET_KEY'], algorithm='HS256')
    
    @staticmethod
    def verify_reset_password(token):
        try:
            id = jwt.decode(token, web_app.config['SECRET_KEY'], algorithms=['HS256'])['user_id']
        except:
            return
        return db.session.get(User, id)


@dataclass    
class Post(db.Model):
    post_id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    body: orm.Mapped[str] = orm.mapped_column(sqla.String(140))
    timestamp: orm.Mapped[Optional[datetime]] = orm.mapped_column(sqla.DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    user_id: orm.Mapped[int] = orm.mapped_column(sqla.ForeignKey(User.id), index=True)

    author: orm.Mapped[Optional[User]] = orm.relationship(back_populates='posts')

    def __repr__(self) -> str:
        return f"Post {self.body}" #this method is defined for developers to easier debug and test the models in the shell
