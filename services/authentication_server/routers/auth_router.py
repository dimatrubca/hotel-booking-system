from typing import List, Union
from fastapi import APIRouter, Depends, HTTPException, Header
from requests import request
from sqlalchemy.orm import Session
import hashlib
from auth_service import register, authenticate, verify as verify_token

from database import SessionLocal, engine
from schemas.auth import AuthSchema
import models
from schemas.client import CreateClient


router = APIRouter(
    prefix="/test",
)

# Dependency
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post("/client")
def create_client(client: CreateClient, db: Session = Depends(get_db)):
    hash_object = hashlib.sha1(bytes(client.client_secret, 'utf-8'))
    hashed_client_secret = hash_object.hexdigest()

    # make a call to the model to authenticate
    create_response =  register(db, client.client_id, hashed_client_secret, client.is_admin)

    return {'success': create_response}


@router.post("/auth")
def auth(auth_data: AuthSchema, db: Session = Depends(get_db)):
    hash_object = hashlib.sha1(bytes(auth_data.client_secret_input, 'utf-8'))
    hashed_client_secret = hash_object.hexdigest()

    authentication = authenticate(db, auth_data.client_id, hashed_client_secret)
    
    if authentication == False:
        return {'success': False}

    return authentication
    
@router.post("/verify")
def verify(authorization: Union[str, None] = Header(default=None)):
    print("authorization:",authorization)
    token = authorization.replace("Bearer ", "")
    verification = verify_token(token)

    return verification


# @router.post("/logout")
# def logout():
#     token = request.form.get("token")
#     status = blacklist(token)

#     return {
#         'success': status
#     }