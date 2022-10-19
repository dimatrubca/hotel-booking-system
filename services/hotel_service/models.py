from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.types import DateTime, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint

from database import Base

# child
class Hotel(Base):
    __tablename__ = "hotels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    stars = Column(Integer)
    country_id = Column(Integer, ForeignKey("countries.id"))
    city_id = Column(Integer, ForeignKey("cities.id"))

    country = relationship("Country", back_populates="hotels")
    city = relationship("City", back_populates="hotels")
    rooms = relationship("Room",  back_populates="hotel")


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    area = Column(Float)
    max_occupancy = Column(Integer)
    floor = Column(Integer)
    hotel_id = Column(Integer, ForeignKey("hotels.id"))
    hotel = relationship("Hotel", back_populates="rooms")



# parent
class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)

    hotels = relationship("Hotel", back_populates="country")


class City(Base):
    __tablename__ = "cities"
    __table_args__ = (
        UniqueConstraint('name', 'country_id', name='unique_city'),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String)
    country_id = Column(Integer, ForeignKey("cities.id"))

    hotels = relationship("Hotel", back_populates="city")



class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))
    user_id = Column(String)
    check_in = Column(DateTime())
    checkout = Column(DateTime())
