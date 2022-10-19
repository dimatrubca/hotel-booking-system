from fastapi import FastAPI
from dotenv import load_dotenv

from database import engine
import models
from routers import auth_router

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router.router)

@app.get("/")
def read_root():
    return {'Hello': 'World'}