from fastapi import FastAPI

from database import engine
import models
from routers import hotels, cities, countries

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(hotels.router)
app.include_router(cities.router)
app.include_router(countries.router)

@app.get("/")
def read_root():
    return {'Hello': 'World'}