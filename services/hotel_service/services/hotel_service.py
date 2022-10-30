import logging
from sqlalchemy.orm import Session

import models
import schemas.hotel as hotel_schemas
import schemas.room as room_schemas

logger = logging.getLogger(__name__)


def get_hotel(db: Session, hotel_id: int):   
    return db.query(models.Hotel).filter(models.Hotel.id == hotel_id).first()


def get_hotels(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Hotel).offset(skip).limit(limit).all()


def create_hotel(db: Session, hotel: hotel_schemas.HotelCreate):
    db_hotel = models.Hotel(name=hotel.name, description=hotel.description, country_id=hotel.country_id, city_id=hotel.city_id, stars=hotel.stars)

    db.add(db_hotel)
    db.commit()
    db.refresh(db_hotel)

    logger.info(f"Hotel id={db_hotel.id} inserted into db")

    return db_hotel


def get_rooms(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Room).offset(skip).limit(limit).all()


def get_hotel_rooms(db: Session, hotel_id, skip: int = 0, limit: int = 100):
    return db.query(models.Room).filter(models.Room.hotel_id == hotel_id).offset(skip).limit(limit).all()


def create_hotel_room(db: Session, room: room_schemas.RoomCreate, hotel_id: int):
    db_room = models.Room(**room.dict(), hotel_id=hotel_id)
    db.add(db_room)
    db.commit()
    db.refresh(db_room)

    return db_room