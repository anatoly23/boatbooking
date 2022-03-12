from pydantic import BaseModel


class Order(BaseModel):
    orderId: int
    boatId: int
    pierId: int
    clientPhone: str
    comment: str
    timeCreated: str
    orderState: int
    minTimeOrder: int


class Id(BaseModel):
    orderId: int
