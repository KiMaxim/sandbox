from typing import Optional 
import sqlalchemy as sqla
import sqlalchemy.orm as orm
from app import db

class User(db.Model):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    login: orm.Mapped[str] = orm.mapped_column(sqla.String(64), unique=True, index=True)
    password_hash: orm.Mapped[Optional[str]] = orm.mapped_column(sqla.String(128))
    
    def __repr__(self) -> str:
        return f"User {self.login}"
