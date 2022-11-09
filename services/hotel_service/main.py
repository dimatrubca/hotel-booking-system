import datetime
from fastapi import FastAPI, Request
from fastapi_utils.tasks import repeat_every

from database import engine
from routers import hotels, cities, countries, reservations
from utils import register_on_service_discovery
import logging, models, settings

models.Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(name)s:%(message)s', datefmt="%m/%d/%Y %I:%M:%S %p")
logger = logging.getLogger(__name__)

app = FastAPI()

start_time = datetime.datetime.now()
requests_count = 0

app.include_router(hotels.router)
app.include_router(cities.router)
app.include_router(countries.router)
app.include_router(reservations.router)

# todo: change logic, if error, retry... sooner
@app.on_event("startup")
# @repeat_every(seconds=settings.SERVICE_DISCOVERY_REQUESTS_PERIOD)  # 1 hour
def check_services_activity_task() -> None:
    register_on_service_discovery()


@app.middleware("http")
async def count_requests(request: Request, call_next):
    global requests_count
    response = await call_next(request)

    requests_count += 1

    return response

@app.get("/status")
def status():
    seconds_running = (datetime.datetime.now() - start_time).total_seconds()

    return {
        'status': 'running',
        'port': settings.PORT,
        'seconds_since_start': seconds_running,
        'processed_requests': requests_count
    }