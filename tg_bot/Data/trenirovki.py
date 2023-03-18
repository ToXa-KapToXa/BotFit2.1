import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Trenirovki(SqlAlchemyBase):
    __tablename__ = 'trenirovki'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    description = sqlalchemy.Column(sqlalchemy.Text)
    result = sqlalchemy.Column(sqlalchemy.Text)

    user_treni = orm.relation('Users')