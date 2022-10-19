from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal, engine
import schemas.country as country_schemas
import schemas.reservation as reservation_schemas
from services import hotel_service
import models, schemas_old


router = APIRouter(
    prefix="/reservations",
)

# Dependency
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_reservation(reservation: reservation_schemas.Country, db: Session = Depends(get_db)):
    # db_hotel = hotel_servce.get
    db_reservation = models.Reservation(**reservation.dict())

    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)

    return db_reservation


@router.get("/", response_model=List[reservation_schemas.Country])
def get_reservations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    reservations = db.query(models.Reservation).offset(skip).limit(limit).all()
    
    return reservations


@router.get("/{reservation_id}", response_model=country_schemas.Reservation)
def get_reservation(reservation_id: int, db: Session = Depends(get_db)):
    reservation = db.query(models.Reservation).filter(models.Reservation.id==reservation_id).first()

    return reservation
