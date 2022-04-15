from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src import crud, schemas

from .urls import manager

router = APIRouter()
from src.core.dependencies import get_db


# @router.post("/list")
# async def mock_order(order: schemas.Body, db: Session = Depends(get_db)):

#     data = {
#         "header": "clientOrderCreated",
#         "body": {
#             "clientPhone": order.clientPhone,
#             "pierId": order.pierId,
#             "orderId": order.orderId,
#             "comment": order.comment,
#         },
#     }
#     client = crud.get_client(db, order.clientPhone)
#     crud.set_order(db, order.comment, client.id, order.pierId, order.boatId)
#     # await manager.broadcast(data)
#     await manager.send_personal_message(data, "+79200000001")
#     return {"status": "ok"}
