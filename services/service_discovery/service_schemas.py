from optparse import Option
from typing import Optional
from pydantic import BaseModel

class RegisterService(BaseModel):
    service_id: str
    name: str
    host: Optional[str]
    port: Optional[int]

class UnregisterService(BaseModel):
    service_id: str