from pydantic import BaseModel


class ReservationBase(BaseModel):
    hotel_id: str
    room_id: str
    check_in: int
    checkout: int
    city_id: int
    user_id: str


class ReservationCreate(HotelBase):
    pass


class Reservtion(HotelBase):
    id: int 

    class Config:
        orm_mode = True