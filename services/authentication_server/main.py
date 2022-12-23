from fastapi import FastAPI
from dotenv import load_dotenv
import logging

from database import engine
import models
from routers import auth_router
from utils import register_on_service_discovery, unregister_on_service_discovery

logging.basicConfig(filename='logs/server.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
                    
logger = logging.getLogger(__name__)

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router.router)


@app.on_event("startup")
def check_services_activity_task() -> None:
    register_on_service_discovery()
    

@app.on_event("shutdown")
def shutdown_event():
    unregister_on_service_discovery()