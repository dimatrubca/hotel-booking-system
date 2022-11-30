import datetime
from pydantic import BaseModel


class ReservationBase(BaseModel):
    hotel_id: str
    room_id: str
    check_in: datetime.datetime
    checkout: datetime.datetime
    user_id: str


class ReservationCreate(ReservationBase):
    pass


class Reservation(ReservationBase):
    id: int 

    class Config:
        orm_mode = True