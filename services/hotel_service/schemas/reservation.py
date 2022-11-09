from pydantic import BaseModel


class ReservationBase(BaseModel):
    hotel_id: str
    room_id: str
    check_in: int
    checkout: int
    city_id: int
    user_id: str


class ReservationCreate(ReservationBase):
    pass


class Reservation(ReservationBase):
    id: int 

    class Config:
        orm_mode = True