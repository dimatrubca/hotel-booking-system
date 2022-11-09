from functools import wraps
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal, engine, get_db
import schemas.country as country_schemas
import schemas.reservation as reservation_schemas
from services import hotel_service
import models, schemas_old

import time


router = APIRouter(
    prefix="/reservations",
)

# todo: check if it works, add response from gateway gateway
MAX_CONCURRENT_TASKS = 5
concurrent_tasks = 0

def limit_concurrent_tasks(f):
    @wraps(f)
    def wrap_function(*args, **kwargs):
        global concurrent_tasks
        global MAX_CONCURRENT_TASKS

        if concurrent_tasks >= MAX_CONCURRENT_TASKS:
            raise HTTPException(status_code=429) #todo: return 429
        
        concurrent_tasks += 1 # mutex? check if is multithreaded fastapi
        result = f(*args, **kwargs)
        concurrent_tasks -= 1

        return result

    return wrap_function


@router.post("/")
@limit_concurrent_tasks
def create_reservation(reservation: reservation_schemas.ReservationCreate, db: Session = Depends(get_db)):
    # db_hotel = hotel_servce.get
    db_reservation = models.Reservation(**reservation.dict())

    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)

    return db_reservation


@router.get("/", response_model=List[reservation_schemas.Reservation])
@limit_concurrent_tasks
def get_reservations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    reservations = db.query(models.Reservation).offset(skip).limit(limit).all()

    time.sleep(1)
    
    return reservations


@router.get("/{reservation_id}", response_model=reservation_schemas.Reservation)
@limit_concurrent_tasks
def get_reservation(reservation_id: int, db: Session = Depends(get_db)):
    reservation = db.query(models.Reservation).filter(models.Reservation.id==reservation_id).first()

    return reservation
