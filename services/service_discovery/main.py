import logging
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from dotenv import load_dotenv

from database import SessionLocal, engine, get_db
from sqlalchemy.orm import Session
from fastapi_utils.tasks import repeat_every
from sqlalchemy.orm.exc import NoResultFound

import models
from service_schemas import RegisterService, UnregisterService
import service
from settings import MAX_INACTIVE_TIME
from utils import check_services_activity

logging.basicConfig(filename='logs/server.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.on_event("startup")
@repeat_every(seconds=MAX_INACTIVE_TIME)  # 1 hour
def check_services_activity_task() -> None:
    check_services_activity(db=get_db())



@app.post("/register")
def register_service(register_service_dto: RegisterService, request:Request, db: Session = Depends(get_db)):
    # todo: add verification id already exists / replace (update timestamp)
    print(request.client.host)
    print(request.client.port)

    register_service_dto.host = register_service_dto.host if register_service_dto.host else request.client.host
    register_service_dto.port = register_service_dto.port if register_service_dto.port else request.client.port

    print(register_service_dto.host, request.client.host)
    print(register_service_dto.port, request.client.port)

    # if register_service_dto.host != request.client.host or register_service_dto.port != request.client.port:
    #     return HTTPException(400, "Host/port mismatch")

    response = service.register_service(register_service_dto, db)

    return response


@app.post("/unregister")
def unregister_service(unregister_service_dto: UnregisterService, request:Request, db: Session = Depends(get_db)):
    try:
        service.unregister_service(unregister_service_dto, db)
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail="Invalid server_id")

    return Response(status_code=204)


@app.get("/services")
def get_services(db: Session = Depends(get_db)):
    services = service.get_all_services(db)

    return services


@app.get("/services/{name}")
def get_service(name:str, db: Session = Depends(get_db)):

    services = service.get_services_by_name(name, db)

    return services

