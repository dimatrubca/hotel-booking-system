from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from functools import wraps

from database import SessionLocal, engine, get_db
# from schemas import hotel as hotel_schemas
# from schemas import room as room_schemas
import schemas.hotel as hotel_schemas
import schemas.room as room_schemas
import logging


from services import hotel_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/hotels",
)


@router.post("/")
def create_hotel(hotel: hotel_schemas.HotelCreate, db: Session = Depends(get_db)):
    # db_hotel = hotel_servce.get
    hotel = hotel_service.create_hotel(db=db, hotel=hotel)

    return hotel


@router.get("/", response_model=List[hotel_schemas.Hotel])
def get_hotels(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    hotels = hotel_service.get_hotels(db, skip=skip, limit=limit)
    
    return hotels


@router.get("/{hotel_id}", response_model=hotel_schemas.Hotel)
def get_hotel(hotel_id: int, db: Session = Depends(get_db)):
    db_hotel = hotel_service.get_hotel(db, hotel_id=hotel_id)

    if db_hotel is None:
        raise HTTPException(status_code=404, detail="Hotel ot found")

    return db_hotel


@router.post("/{hotel_id}/rooms", response_model=room_schemas.Room)
def create_room_for_hotel(
    hotel_id: int, room: room_schemas.RoomCreate, db: Session = Depends(get_db)
):
    return hotel_service.create_hotel_room(db=db, room=room, hotel_id=hotel_id)



@router.get("/{hotel_id}/rooms", response_model=List[room_schemas.Room])
def get_hotel_rooms(hotel_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return hotel_service.get_hotel_rooms(db, hotel_id=hotel_id, skip=skip, limit=limit)


@router.get("/rooms/", response_model=List[room_schemas.Room])
def read_rooms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    rooms = hotel_service.get_rooms(db, skip=skip, limit=limit)

    return rooms