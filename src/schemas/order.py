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


from pydantic import BaseModel


class TypePayment(BaseModel):
    typePayment: int
    idCard: int


class SetOrder(BaseModel):
    idBoat: int
    idPier: int
    comment: str
    typePayment: TypePayment
    minTimeOrder: int
