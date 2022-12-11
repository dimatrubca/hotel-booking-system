
import datetime
from fastapi import Request
from service_schemas import RegisterService, UnregisterService
from sqlalchemy.orm import Session

import models

def register_service(service: RegisterService, db: Session):
    service_db:models.Service = db.query(models.Service).filter((models.Service.id == service.service_id)).first()
    host_port_exists = db.query(models.Service).filter((models.Service.host == service.host) & (models.Service.port == service.port)).first() != None
        
    if not service_db and  host_port_exists:
        raise Exception("Host/port already registered with another id")
    elif service_db:
        if service_db.host != service.host or service_db.port != service.port:
            raise Exception(f"Service with id {service_db.id} registered on {service_db.host}:{service_db.port}")
        
        service_db.updated_at = datetime.datetime.now()
        db.commit()
        db.refresh(service_db)

        print("updated...")

        return service_db

    service_db = models.Service(id=service.service_id, name=service.name, host=service.host, port=service.port, protocol=service.protocol)
    db.add(service_db)
    db.commit()
    db.refresh(service_db)

    return service_db


def unregister_service(unregister_service_dto: UnregisterService, db: Session):
    service_db = db.query(models.Service).filter(models.Service.id == unregister_service_dto.service_id).one()

    db.delete(service_db)
    db.commit()


def get_all_services(db: Session):
    services = db.query(models.Service).all()

    services_map = {}

    for service in services:
        if service.name not in services_map:
            services_map[service.name] = []
        
        services_map[service.name].append(service.__dict__) #todo: check

    return services_map


def get_services_by_name(name: str, db: Session):
    services = db.query(models.Service).filter(models.Service.name == name).all()

    return services

