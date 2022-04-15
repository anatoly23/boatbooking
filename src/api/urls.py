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
client_manager = ConnectionManager()
boatmanager = BoatManager()


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


@router.websocket("/ws/wscoords")
async def coords_endpoit(websocket: WebSocket):
    await boatmanager.connect(websocket)
    try:
        while True:
            res = await websocket.receive_json()
            print(res)

    except WebSocketDisconnect:
        boatmanager.disconnect(websocket)


@router.websocket("/ws/client")
async def websocket_endpoint(
    websocket: WebSocket,
    db: Session = Depends(get_db),
    client: schemas.Client = Depends(get_user_from_header),
):
    await client_manager.connect(websocket, client.phone)
    try:
        while True:
            res = await websocket.receive_json()
    except WebSocketDisconnect:
        manager.disconnect(client.phone)


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


@router.get(
    "/piers/info/{pierId}",
    dependencies=[Depends(get_user_from_header)],
    tags=["customer"],
)
async def piers_info(pierId, db: Session = Depends(get_db)):
    pier = crud.get_pier(db, pierId)
    images = crud.get_pier_images(db, pierId)
    image_list = [i.image for i in images]
    result = {
        "id": pier.id,
        "name": pier.name,
        "rating": pier.rating,
        "coordinates": {"lat": pier.lat, "lon": pier.lon},
        "images": image_list,
        "description": pier.description,
    }

    return result


@router.get(
    "/boat/info/{boatId}",
    dependencies=[Depends(get_user_from_header)],
    tags=["customer"],
)
async def boat_info(boatId, db: Session = Depends(get_db)):
    boat = crud.get_boat_by_id(db, boatId)
    images = crud.get_images(db, boat.id)
    image_list = [i.image for i in images]
    captain = crud.get_captain(db, boat.captain_id)
    result = {
        "id": boat.id,
        "name": boat.name,
        "rating": boat.boat_raiting,
        "images": image_list,
        "description": boat.description,
        "cost": boat.cost,
        "captain": {"name": captain.name, "rating": captain.raiting},
        "length": boat.length,
        "power": boat.power,
        "capacity": boat.capacity,
    }

    return result


@router.post("/order/client/create", tags=["customer"])
async def set_client_order(
    order: schemas.SetOrder,
    db: Session = Depends(get_db),
    client: schemas.Client = Depends(get_user_from_header),
):
    client = crud.get_client(db, client.phone)
    order = crud.set_order(
        db, order.comment, client.id, order.idPier, order.idBoat, order.minTimeOrder
    )

    data = {
        "header": "clientOrderCreated",
        "body": {
            "clientPhone": client.phone,
            "pierId": order.pier_id,
            "orderId": order.id,
            "comment": order.comment,
        },
    }
    boat = crud.get_boat_by_id(db, order.boat_id)
    captain = crud.get_captain(db, boat.captain_id)
    await manager.send_personal_message(data, captain.phone)
    return {"orderId": order.id}


@router.post(
    "/order/client/reject",
    status_code=201,
    dependencies=[Depends(get_user_from_header)],
    tags=["customer"],
)
async def client_reject(orderId, db: Session = Depends(get_db)):
    crud.set_customer_reject(db, orderId)

    data = {"header": "ClientOrderRejected", "body": {"orderId": orderId}}
    order = crud.get_order_by_id(db, orderId)
    boat = crud.get_boat_by_id(db, order.boat_id)
    captain = crud.get_captain(db, boat.captain_id)
    await manager.send_personal_message(data, captain.phone)


@router.get("/order/client/history", tags=["customer"])
async def client_history(
    client: schemas.Client = Depends(get_user_from_header),
    db: Session = Depends(get_db),
):
    client = crud.get_client(db, client.phone)
    # client = crud.get_client(db, "+79253452562")
    dates = crud.get_ordedrs_by_date(db, client.id)

    data = {
        "history": [
            {
                "date": date[1],
                "orders": [
                    {
                        "orderId": order[0].id,
                        "time": order[0].time_created.strftime("%H:%M"),
                        "boatName": order[1].name,
                        "boatId": order[1].id,
                        "captain": order[2].name,
                        "cost": order[1].cost,
                    }
                    for order in crud.get_orders_by_time(db, client.id, date[1])
                ],
            }
            for date in dates
        ]
    }

    return data


@router.get("/order/client/current", tags=["customer"])
async def client_current(
    client: schemas.Client = Depends(get_user_from_header),
    db: Session = Depends(get_db),
):

    try:
        client = crud.get_client(db, client.phone)
        # client = crud.get_client(db, "+79253452562")
        order = crud.get_current_order(db, client.id)
        boat = crud.get_boat_by_id(db, order.boat_id)
        boat_images = crud.get_images(db, boat.id)
        boat_image_list = [i.image for i in boat_images]
        boat_coord = crud.get_boat_coordinates(db, boat.id)
        captain = crud.get_boat_by_id(db, boat.captain_id)
        piers = crud.get_piers(db, boat.id)
        piers_list = [pier.id for pier in piers]
        current_pier = crud.get_pier(db, order.pier_id)
        pier_images = crud.get_pier_images(db, current_pier.id)
        pier_image_list = [i.image for i in pier_images]

        data = {
            "orderId": order.id,
            "boat": {
                "id": boat.id,
                "name": boat.name,
                "rating": boat.boat_raiting,
                "images": boat_image_list,
                "cost": boat.cost,
                "captain": {"name": captain.name, "rating": captain.raiting},
                "coordinates": {
                    "lat": boat_coord.latitude,
                    "lon": boat_coord.longtitude,
                },
                "piers": [piers_list],
            },
            "pier": {
                "id": current_pier.id,
                "name": current_pier.name,
                "rating": current_pier.rating,
                "coordinates": {"lat": current_pier.lat, "lon": current_pier.lon},
                "images": pier_image_list,
            },
            "captainPhone": captain.phone,
            "timeCreated": order.time_created,
            "orderState": order.order_state,
            "minTimeOrder": order.minTimeOrder,
        }
        return data
    # todo уточнить что отлавливаем
    except:
        raise HTTPException(status_code=400, detail="Fail")


@router.post(
    "/piers", tags=["customer"]
)  # dependencies=[Depends(get_user_from_header)],)
async def get_pier(
    # version: int,
    db: Session = Depends(get_db),
):

    piers = crud.get_piers_all(db)

    piers_list = [
        {
            "id": pier.id,
            "name": pier.name,
            "rating": pier.rating,
            "coordinates": {"lat": pier.lat, "lon": pier.lon},
            "images": [i.image for i in crud.get_pier_images(db, pier.id)],
        }
        for pier in piers
    ]

    return {
        "version": 2,
        "piers": piers_list,
    }
