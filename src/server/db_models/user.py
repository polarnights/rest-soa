import enum

from sqlalchemy import Column, Enum, Integer, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Sex(enum.Enum):
    male = 1
    female = 2
    other = 3


class User(Base):
    __tablename__ = "user"

    username = Column(String, primary_key=True)
    avatar_path = Column(String)
    sex = Column(Enum(Sex))
    token = Column(String)
    session_count = Column(Integer, default=0)
    win_count = Column(Integer, default=0)
    lose_count = Column(Integer, default=0)
    time = Column(Integer, default=0)
