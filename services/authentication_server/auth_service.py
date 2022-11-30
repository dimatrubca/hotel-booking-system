import logging
from this import d
from dotenv import load_dotenv
from sqlalchemy.orm import Session
import os
from auth_response import AuthResponse
import jwt

from auth_payload import AuthPayload
import models

load_dotenv()

AUTHSECRET = os.getenv("AUTHSECRET")
EXPIRESSECONDS = os.getenv("EXPIRESSECONDS")

logger = logging.getLogger(__name__)

def authenticate(db: Session, client_id, client_secret):
    client = db.query(models.Client).filter((models.Client.client_id == client_id) & (models.Client.client_secret == client_secret)).first() #todo: handle if none

    if client == None: #???
        return False

    payload = AuthPayload(client.id, client.client_id, client.is_admin)
    print(payload.__dict__, AUTHSECRET)
    encoded_jwt = jwt.encode(payload.__dict__, AUTHSECRET, algorithm='HS256')
    print(encoded_jwt)
    print(type(encoded_jwt))
    response = AuthResponse(encoded_jwt, EXPIRESSECONDS, client.is_admin)
    
    return response.__dict__


def verify(token):
    try:
        decoded = jwt.decode(token, AUTHSECRET, algorithms=['HS256'])
        logger.info(f"token {token} verified")
        return decoded
    except Exception as error:
        print(error)
        logger.info(f"token {token} invalid")

        return {'success': False}


def register(db: Session, client_id, client_secret, is_admin):
    print("inside register")
    client = models.Client(client_id=client_id, client_secret=client_secret, is_admin=is_admin)
    db.add(client)
    db.commit()
    db.refresh(client)
    print("finished")

    return client
