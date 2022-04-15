from pydantic import BaseModel


class Client(BaseModel):
    phone: str
