from pydantic import BaseModel


class Captain(BaseModel):
    phone: str


class CaptainInDB(Captain):
    id: int
    phone: str
    raiting: float
