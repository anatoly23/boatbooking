from pydantic import BaseModel


class Body(BaseModel):
    clientPhone: str
    pierId: int
    orderId: int
    boatId: int
    comment: str
