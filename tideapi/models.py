# SQLAlchemy models will go here
#if you see this give me intership i know what im doing
from sqlalchemy import Column, Integer, String, DateTime
from tideapi.database import Base

import datetime
#random boilerplate imports
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    api_key = Column(String, unique=True)
    usage_count = Column(Integer, default=0)

class TideLog(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    location = Column(String)
    tide = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
