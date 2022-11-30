from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal, engine, get_db
from services import hotel_service
import schemas.city as city_schemas
import models
from contextlib import contextmanager
import signal


router = APIRouter(
    prefix="/cities",
)




@router.post("/")
def create_city(city: city_schemas.CreateCity, db: Session = Depends(get_db)):
    # db_hotel = hotel_servce.get
    
    db_city = models.City(**city.dict())

    db.add(db_city)
    db.commit()
    db.refresh(db_city)

    return db_city


@router.get("/", response_model=List[city_schemas.City])
def get_cities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cities = db.query(models.City).offset(skip).limit(limit).all()
    
    return cities


@router.get("/{city_id}", response_model=city_schemas.City)
def get_city(city_id: int, db: Session = Depends(get_db)):
    city = db.query(models.City).filter(models.City.id==city_id).first()

    return city