from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal, engine
import schemas.country as country_schemas
from services import hotel_service
import models, schemas_old


router = APIRouter(
    prefix="/countries",
)

# Dependency
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_country(country: country_schemas.CreateCountry, db: Session = Depends(get_db)):
    # db_hotel = hotel_servce.get
    db_country = models.Country(**country.dict())

    db.add(db_country)
    db.commit()
    db.refresh(db_country)

    return db_country


@router.get("/", response_model=List[country_schemas.Country])
def get_countries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    countries = db.query(models.Country).offset(skip).limit(limit).all()
    print("countries:")
    print(countries)
    
    return countries


@router.get("/{country_id}", response_model=country_schemas.Country)
def get_country(country_id: int, db: Session = Depends(get_db)):
    city = db.query(models.Country).filter(models.Country.id==country_id).first()

    return city
