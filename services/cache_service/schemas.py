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


class ElectionMessage(BaseModel):
    replication_id: str
    replication_offset: int
    node_id: str



class LeaderUpdated(BaseModel):
    host: str
    replication_id: str
    offset: int
    secondary_id: str
    secondary_offset: int