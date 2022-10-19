from enum import unique
from sqlalchemy import VARCHAR, Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.types import DateTime, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint

from database import Base

from database import Base

class Client(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    client_id = Column(VARCHAR(128), unique=True)
    client_secret = Column(Integer)
    is_admin = Column(String)


