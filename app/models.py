from typing import Optional 
import sqlalchemy as sqla
import sqlalchemy.orm as orm
from app import db
from datetime import datetime, timezone

class User(db.Model):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    login: orm.Mapped[str] = orm.mapped_column(sqla.String(64), unique=True, index=True)
    email: orm.Mapped[str] = orm.mapped_column(sqla.String(120), unique=True, index=True)
    password_hash: orm.Mapped[Optional[str]] = orm.mapped_column(sqla.String(128))

    posts: orm.WriteOnlyMapped['Post'] = orm.relationship('Post', back_populates='author', lazy='dynamic')

    def __repr__(self) -> str:
        return f"User {self.login}"
    
class Post(db.Model):
    post_id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    body: orm.Mapped[str] = orm.mapped_column(sqla.String(140))
    timestamp: orm.Mapped[Optional[str]] = orm.mapped_column(sqla.DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    user_id: orm.Mapped[int] = orm.mapped_column(sqla.ForeignKey(User.id), index=True)

    author: orm.Mapped[User] = orm.relationship(back_populates='posts')

    def __repr__(self) -> str:
        return f"Post {self.body}"
