from pydoc import cli
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src import crud, schemas

# from .clienturls import captain_manager

from ..core.manager import client_manager, captain_manager

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


@router.get("/list")
async def get_websocket():
    await client_manager.list_ws()
    # await captain_manager.list_ws()
    # client_manager.disconnect("+79253452562")
    # data = {
    #     "header": "boatsOnMap",
    #     "body": {
    #         "boats": [
    #             {
    #                 "id": 1,
    #                 "name": "Monna liza",
    #                 "rating": 4.32,
    #                 "images": ["https://itboat.com/uploads/e2f5/e25491600fdf.jpg"],
    #                 "cost": 15000,
    #                 "captain": {"name": "Семен Семеныч", "rating": 4.92},
    #                 "coordinates": {"lat": 59.954335, "lon": 30.380765},
    #                 "piers": [1, 2],
    #             }
    #         ]
    #     },
    # }

    data = {
        "header": "currentOrderInfo",
        "body": {
            "orderId": 2,
            "boatCoordinates": {
                "lat": 59.9225033333333,
                "lon": 30.1791616666667,
            },
            "boatId": 1,
            "pierId": 1,
            "approximateArrivalTime": "15:00",
        },
    }
    await client_manager.broadcast(data)
    # await client_manager.send_personal_message(data, "+79200000009")
    return {"status": "ok"}


@router.get("/disconnect")
async def dis():
    client_manager.disconnect("+79253452562")
