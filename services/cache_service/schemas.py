from typing import Union
from pydantic import BaseModel
from datetime import datetime

class Event(BaseModel):
    operation: str # enum, rename to type?
    service: str
    key: str
    value: str
    expiration_time: Union[datetime, None]
    offset: int
