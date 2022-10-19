from pydantic import BaseModel


class BaseClient(BaseModel):
    client_id: str
    client_secret: str #todo: move to create????
    is_admin: bool


class CreateClient(BaseClient):
    pass


class Client(CreateClient):
    id: int 

    class Config:
        orm_mode = True