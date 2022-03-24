from sqlalchemy.orm import Session

from src import crud, schemas
from src.core.manager import BoatManager, ConnectionManager
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

manager = ConnectionManager()
boatmanager = BoatManager()


@router.post("/order/captain/reject", dependencies=[Depends(get_user_from_header)])
async def capitan_reject(
    order_id: schemas.Id,
    db: Session = Depends(get_db),
):
    crud.set_captain_reject(db, order_id.orderId)


@router.get("/captain/appointment", response_model=schemas.Boat)
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
)
async def capitan_complete(order_id: schemas.Id, db: Session = Depends(get_db)):
    crud.set_capitan_complete(db, order_id.orderId)


@router.post(
    "/order/captain/accepted",
    status_code=201,
    dependencies=[Depends(get_user_from_header)],
)
async def capitan_accepted(
    order_id: schemas.Id,
    db: Session = Depends(get_db),
):
    crud.set_captain_accept(db, order_id.orderId)


@router.get("/order/captain/current", response_model=schemas.Order)
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


@router.websocket("/ws/wscoords")
async def coords_endpoit(websocket: WebSocket):
    await boatmanager.connect(websocket)
    try:
        while True:
            res = await websocket.receive_json()
            print(res)

    except WebSocketDisconnect:
        boatmanager.disconnect(websocket)


@router.websocket("/ws/captain")
async def websocket_endpoint(
    websocket: WebSocket,
    db: Session = Depends(get_db),
    captain: schemas.Captain = Depends(get_user_from_header),
):
    await manager.connect(websocket, captain.phone)
    try:
        while True:
            res = await websocket.receive_json()
            # print(res['body']['coordinates']['longitude'])

            capitan = crud.get_user_by_phone(db, captain.phone)
            boat = crud.get_boat(db, capitan.id)

            longitude = res["body"]["coordinates"]["longitude"]
            latitude = res["body"]["coordinates"]["latitude"]
            state = res["body"]["state"]

            crud.set_boat_coordinate(
                db=db,
                longitude=longitude,
                latitude=latitude,
                state=state,
                boat_id=boat.id,
            )
            print(f"ID лодки {boat.id}")
            await boatmanager.broadcast(
                {"longitude": longitude, "latitude": latitude, "boat_id": boat.id}
            )
            # await manager.list_capitans()
    except WebSocketDisconnect:
        manager.disconnect(captain.phone)
