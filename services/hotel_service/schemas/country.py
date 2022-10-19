from pydantic import BaseModel


class BaseCountry(BaseModel):
    name: str


class CreateCountry(BaseCountry):
    pass


class Country(BaseCountry):
    id: int 

    class Config:
        orm_mode = True