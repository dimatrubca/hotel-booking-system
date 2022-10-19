from pydantic import BaseModel

class AuthSchema(BaseModel):
    client_id: str
    client_secret_input: str


# class VerificationSchema:

