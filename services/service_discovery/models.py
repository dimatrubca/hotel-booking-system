from email.policy import default
from enum import unique
from sqlalchemy import VARCHAR, Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.types import DateTime, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint
from sqlalchemy.sql import func


from database import Base


class Service(Base):
    __tablename__ = "services"
    __table_args__ = (UniqueConstraint('host', 'port', name='_host_port_uc'),)

    id = Column(String, primary_key=True, autoincrement=False, nullable=False)
    name = Column(VARCHAR(128))
    protocol = Column(String)
    host = Column(String)
    port = Column(Integer)
    registred_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)

