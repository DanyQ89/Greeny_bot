from .database import SqlAlchemyBase
from sqlalchemy import Column, String, LargeBinary, Float, Boolean, Integer
from sqlalchemy import Date


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(String, unique=True, index=True)
    username = Column(String, unique=True)
    language = Column(String)
    name = Column(String)
    age = Column(Integer)
    height = Column(Integer)
    coord_x = Column(Float)
    coord_y = Column(Float)
    photos = Column(String, default='')
    mainText = Column(String, nullable=True)
    gender = Column(String)
    find_gender = Column(String)
    minAge = Column(Integer)
    maxAge = Column(Integer)
    minHeight = Column(Integer)
    maxHeight = Column(Integer)
    arr_of_ids = Column(LargeBinary)
    arr_of_liked_ids = Column(LargeBinary)
    city = Column(String)
    last_user_id = Column(String)
    last_last_user_id = Column(String)
    premium = Column(Boolean, default=False)
    end_premium = Column(Date, nullable=True)
    premium_like = Column(Integer, default=0)
    premium_back = Column(Integer, default=0)
    active = Column(Boolean, default=True)
