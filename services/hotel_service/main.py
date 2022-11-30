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
logging.basicConfig(filename='logs/hotel_service.log',
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

# @app.get("/")
# def read_root():
#     return {'Hello': 'World'}

# def raise_timeout(_, frame):
#     raise TimeoutError

# @contextmanager
# def timeout_after(seconds: int):
#     print("inside decorator")
#     print(f"on decorator: {threading.get_ident() }")
#     # Register a function to raise a TimeoutError on the signal.
#     # signal.signal(signal.SIGALRM, raise_timeout)
#     # Schedule the signal to be sent after `seconds`.
#     # signal.alarm(seconds)

#     try:
#         yield
#     finally:
#         pass
#         # Unregister the signal so it won't be triggered if the timeout is not reached.
#         # signal.signal(signal.SIGALRM, signal.SIG_IGN)



# @app.get("/test")
# @timeout_after(1)
# async def test():
#     print("before sleep")
#     print(f"on request2: {threading.get_ident() }")
#     await asyncio.sleep(3)
    
#     return {"hello": "world"}


# def timeout(timeout):
#     def deco(func):
#         @functools.wraps(func)
#         def wrapper(*args, **kwargs):
#             res = [Exception('function [%s] timeout [%s seconds] exceeded!' % (func.__name__, timeout))]
#             def newFunc():
#                 try:
#                     res[0] = func(*args, **kwargs)
#                 except Exception as e:
#                     res[0] = e

#             t = threading.Thread(target=newFunc)
#             t.daemon = True
#             try:
#                 t.start()
#                 t.join(timeout)
#             except Exception as je:
#                 raise je
#             ret = res[0]
#             if isinstance(ret, BaseException):
#                 raise ret

#             return ret
#         return wrapper
#     return deco

# def raise_to():
#     print("timeout...")
#     raise HTTPException(status_code=408)

# @app.get('/test2')
# async def test2(timer: int, sleep: int):
#     start = threading.Timer(timer, raise_to)
#     start.start()

#     print(f"going to sleep for {sleep} seconds")
#     time.sleep(sleep)

#     return {"success": True}


# def handle_timeout(sig, frame):
#     raise TimeoutError('took too long')

# @app.get('/test4')
# async def test4(sleep: int):
#     func = timeout(timeout=1)(lambda: time.sleep(sleep))

#     try:
#         func()
#     except Exception as e:
#         return {'status': 'error'}

#     return {'status': 'success'}

    

# @app.get('/test3')
# async def test3(timer: int, sleep: int):
#     try:
#         signal.signal(signal.SIGALRM, handle_timeout)
#         signal.alarm(timer)

#         print(f"going to sleep for {sleep} seconds")
#         time.sleep(sleep)
#         signal.alarm(0)
#     except Exception as e:
#         print(e)

#     return {"success": True}
