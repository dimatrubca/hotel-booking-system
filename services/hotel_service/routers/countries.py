from contextlib import contextmanager
import signal
import time
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal, engine, get_db
import schemas.country as country_schemas
from services import hotel_service
import models, schemas_old


router = APIRouter(
    prefix="/countries",
)

@router.post("/")
def create_country(country: country_schemas.CreateCountry, db: Session = Depends(get_db)):
    # db_hotel = hotel_servce.get
    db_country = models.Country(**country.dict())

    db.add(db_country)
    db.commit()
    db.refresh(db_country)

    return db_country



@contextmanager
def timeout_after(seconds: int):
    print(f"inside timeout_after {seconds} s")

    # Register a function to raise a TimeoutError on the signal.
    signal.signal(signal.SIGALRM, raise_timeout)
    # Schedule the signal to be sent after `seconds`.
    signal.alarm(seconds)

    try:
        yield
    finally:
        # Unregister the signal so it won't be triggered if the timeout is not reached.
        signal.signal(signal.SIGALRM, signal.SIG_IGN)

def raise_timeout(_, frame):
    raise TimeoutError

# Used as such:
@router.get("/", response_model=List[country_schemas.Country])
@timeout_after(5)
def get_countries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    countries = db.query(models.Country).offset(skip).limit(limit).all()
    print("countries:")
    time.sleep(10)
    print(countries)
    
    return countries


@router.get("/{country_id}", response_model=country_schemas.Country)
def get_country(country_id: int, db: Session = Depends(get_db)):
    city = db.query(models.Country).filter(models.Country.id==country_id).first()

    return city
