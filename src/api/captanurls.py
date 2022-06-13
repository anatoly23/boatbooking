from pprint import pprint
from sqlalchemy.orm import Session

from src import crud, schemas
from src.core.manager import captain_manager, boatmanager, client_manager
from src.core.dependencies import (
    get_db,
    get_user_from_header,
)

from fastapi import (
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    APIRouter,
)

router = APIRouter()


@router.post(
    "/order/captain/reject",
    status_code=201,
    dependencies=[Depends(get_user_from_header)],
    tags=["captain"],
)
async def capitan_reject(
    order_id: schemas.Id,
    db: Session = Depends(get_db),
):
    crud.set_captain_reject(db, order_id.orderId)
    order = crud.get_order_by_id(db, order_id.orderId)
    client = crud.get_client_by_id(db, order.client_id)
    data = {
        "header": "CaptainOrderRejected",
        "body": {"orderId": int(order_id.orderId)},
    }
    await client_manager.send_personal_message(data, client.phone)
    # await client_manager.broadcast(data)


@router.get("/captain/appointment", response_model=schemas.Boat, tags=["captain"])
async def capitan_appointment(
    captain: schemas.Captain = Depends(get_user_from_header),
    db: Session = Depends(get_db),
):
    capitan = crud.get_user_by_phone(db, captain.phone)
    boat = crud.get_boat(db, capitan.id)
    if boat:
        images = crud.get_images(db, boat.id)
        image_list = [i.image for i in images]
        piers = crud.get_piers(db, boat.id)

        piers_list = [
            schemas.Pier(
                id=pier.id,
                name=pier.name,
                coordinates=schemas.Coordinates(lat=pier.lat, lon=pier.lon),
            )
            for pier in piers
        ]

        results = schemas.Boat(
            id=boat.id,
            name=boat.name,
            boat_rating=boat.boat_raiting,
            captian_rating=capitan.raiting,
            images=image_list,
            cost=boat.cost,
            piers=piers_list,
        )

        return results
    raise HTTPException(status_code=400, detail="Acess denied")


@router.post(
    "/order/captain/complete",
    status_code=201,
    dependencies=[Depends(get_user_from_header)],
    tags=["captain"],
)
async def capitan_complete(order_id: schemas.Id, db: Session = Depends(get_db)):
    crud.set_capitan_complete(db, order_id.orderId)

    order = crud.get_order_by_id(db, order_id.orderId)
    client = crud.get_client_by_id(db, order.client_id)

    data = {"header": "CaptainCompletedOrder", "body": {"orderId": order_id.orderId}}

    await client_manager.send_personal_message(data, client.phone)


@router.post(
    "/order/captain/accepted",
    status_code=201,
    dependencies=[Depends(get_user_from_header)],
    tags=["captain"],
)
async def capitan_accepted(
    order_id: schemas.Id,
    db: Session = Depends(get_db),
):
    crud.set_captain_accept(db, order_id.orderId)
    order = crud.get_order_by_id(db, order_id.orderId)
    boat = crud.get_boat_by_id(db, order.boat_id)
    captain = crud.get_captain(db, boat.captain_id)
    client = crud.get_client_by_id(db, order.client_id)
    data = {
        "header": "orderAccepted",
        "body": {"orderId": int(order.id), "captainPhone": captain.phone},
    }
    await client_manager.send_personal_message(data, client.phone)
    # await client_manager.broadcast(data)


@router.get("/order/captain/current", response_model=schemas.Order, tags=["captain"])
async def capitan_current(
    captain: schemas.Captain = Depends(get_user_from_header),
    db: Session = Depends(get_db),
):

    capitan = crud.get_user_by_phone(db, captain.phone)
    boat = crud.get_boat(db, capitan.id)
    order = crud.get_order(db, boat.id)
    if order is None:
        raise HTTPException(status_code=400, detail="Acess denied")
    client = crud.get_client_by_id(db, order.client_id)

    return schemas.Order(
        orderId=order.id,
        boatId=order.boat_id,
        pierId=order.pier_id,
        clientPhone=client.phone,
        comment=order.comment,
        timeCreated=str(order.time_created),
        orderState=order.order_state,
        minTimeOrder=order.minTimeOrder,
    )


@router.websocket("/ws/captain")
async def websocket_endpoint(
    websocket: WebSocket,
    db: Session = Depends(get_db),
    captain: schemas.Captain = Depends(get_user_from_header),
):
    await captain_manager.connect(websocket, captain.phone)
    try:
        while True:
            res = await websocket.receive_json()
            # pprint(res)

            capitan = crud.get_user_by_phone(db, captain.phone)
            boat = crud.get_boat(db, capitan.id)

            longitude = res["body"]["coordinates"]["longitude"]
            latitude = res["body"]["coordinates"]["latitude"]
            state = res["body"]["state"]
            boat_speed = res["body"]["coordinates"]["speed"]

            crud.set_boat_coordinate(
                db=db,
                longitude=longitude,
                latitude=latitude,
                state=state,
                boat_id=boat.id,
                boat_speed=boat_speed,
            )
            # print(f"ID лодки {boat.id}")
            await boatmanager.broadcast(
                {
                    "longitude": longitude,
                    "latitude": latitude,
                    "boat_id": boat.id,
                    "status": "connected",
                }
            )
    except WebSocketDisconnect:
        await boatmanager.broadcast(
            {
                "longitude": longitude,
                "latitude": latitude,
                "boat_id": boat.id,
                "status": "disconnected",
            }
        )
        crud.set_boat_coordinate(
            db=db,
            longitude=longitude,
            latitude=latitude,
            state=0,
            boat_id=boat.id,
            boat_speed=boat_speed,
        )
        captain_manager.disconnect(captain.phone)
