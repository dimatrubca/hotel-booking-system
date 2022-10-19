from pydantic import BaseModel


class BaseCity(BaseModel):
    name: str
    country_id: int


class CreateCity(BaseCity):
    pass


class City(BaseCity):
    id: int 

    class Config:
        orm_mode = True