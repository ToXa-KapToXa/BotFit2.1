import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Users(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    tg_id = sqlalchemy.Column(sqlalchemy.Integer)
    first_name = sqlalchemy.Column(sqlalchemy.Text)

    treni = orm.relation("Trenirovki", back_populates="user_treni")