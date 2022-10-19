from pydantic import BaseModel


class RoomBase(BaseModel):
    area: float
    max_occupancy: int
    floor: int



class RoomCreate(RoomBase):
    pass


class Room(RoomBase):
    id: int
    hotel_id: int

    class Config:
        orm_mode = True




