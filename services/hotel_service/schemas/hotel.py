from pydantic import BaseModel


class HotelBase(BaseModel):
    name: str
    description: str
    stars: int
    country_id: int
    city_id: int


class HotelCreate(HotelBase):
    pass


class Hotel(HotelBase):
    id: int 

    class Config:
        orm_mode = True