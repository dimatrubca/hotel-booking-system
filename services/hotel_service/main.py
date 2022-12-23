import datetime
import time
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi import FastAPI

from database import engine
from routers import hotels, cities, countries, reservations
from utils import register_on_service_discovery, unregister_on_service_discovery
import logging, models, settings


models.Base.metadata.create_all(bind=engine)

# logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(name)s:%(message)s', datefmt="%m/%d/%Y %I:%M:%S %p")
logging.basicConfig(filename='logs/server.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)


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
def check_services_activity_task() -> None:
    register_on_service_discovery()

    # uvicorn_logger = logging.getLogger('uvicorn.access')
    # handler = logging.FileHandler(filename='logs/server.log', mode='a')
    # handler.setFormatter(logging.Formatter(fmt='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S'))

    # uvicorn_logger.addHandler(handler)

@app.on_event("shutdown")
def shutdown_event():
    unregister_on_service_discovery()


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

@app.get("/error")
def error_test(n: int = Query(default=0)):
    if n == 1:
        raise HTTPException(status_code=500)
    return {'success': True}