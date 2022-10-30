from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every

from database import engine
from routers import hotels, cities, countries
from utils import register_on_service_discovery
import logging, models, settings

models.Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(name)s:%(message)s', datefmt="%m/%d/%Y %I:%M:%S %p")
logger = logging.getLogger(__name__)

app = FastAPI()

app.include_router(hotels.router)
app.include_router(cities.router)
app.include_router(countries.router)

# todo: change logic, if error, retry... sooner
@app.on_event("startup")
# @repeat_every(seconds=settings.SERVICE_DISCOVERY_REQUESTS_PERIOD)  # 1 hour
def check_services_activity_task() -> None:
    register_on_service_discovery()

@app.get("/")
def read_root():
    return {'Hello': 'World'}