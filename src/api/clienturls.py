from geographiclib.geodesic import Geodesic
import datetime
from sqlalchemy.orm import Session
from shapely.geometry import Point, Polygon, LineString
from src import crud, schemas
from src.core.manager import captain_manager, client_manager
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
    BackgroundTasks,
)

from anyio import sleep


router = APIRouter()


async def send_notification(client_phone: str, order_id, db: Session = Depends(get_db)):
    print("Задача прилетела")
    geod = Geodesic.WGS84
    print(client_phone)
    order = crud.get_order_by_id(db, order_id)
    pier = crud.get_pier(db, order.pier_id)
    count = 0
    while count < 5:
        coord = crud.get_boat_coordinates(db, order.boat_id)
        # distance = LineString([(coord.latitude, coord.longitude), (pier.lat, pier.lon)])
        distance = geod.Inverse(coord.latitude, coord.longitude, pier.lat, pier.lon)

        print(coord.boat_speed)
        print(distance["s12"])
        if coord.boat_speed == 0.0:
            print("Скорость нулевая")
            apparrivaltime = distance["s12"] / 1
        else:
            print("Скорость не нулевая")
            apparrivaltime = distance["s12"] / coord.boat_speed
        apparrivaltime = str(datetime.timedelta(seconds=apparrivaltime)).split(":")

        data = {
            "header": "currentOrderInfo",
            "body": {
                "orderId": str(order_id),
                "boatCoordinates": {
                    "lat": coord.latitude,
                    "lon": coord.longitude,
                },
                "boatId": order.boat_id,
                "pierId": order.pier_id,
                "approximateArrivalTime": f"{apparrivaltime[0]}:{apparrivaltime[1]}",
            },
        }
        await client_manager.send_personal_message(data, client_phone)
        count += 1
        print(count)
        await sleep(10)
    print("Задача отработала")


@router.websocket("/ws/client")
async def websocket_endpoint(
    background_tasks: BackgroundTasks,
    websocket: WebSocket,
    db: Session = Depends(get_db),
    client: schemas.Client = Depends(get_user_from_header),
):
    await client_manager.connect(websocket, client.phone)
    try:
        while True:
            res = await websocket.receive_json()
            # pprint(res)

            if res["header"] == "getBoats":
                boats_coords = crud.get_boats_coordinates(db)
                boats_all = [
                    crud.get_boat_on_map(db, boat.boat_id) for boat in boats_coords
                ]
                coords = [
                    (res["body"]["northWest"]["lat"], res["body"]["northWest"]["lon"]),
                    (res["body"]["northEast"]["lat"], res["body"]["northEast"]["lon"]),
                    (res["body"]["southEast"]["lat"], res["body"]["southEast"]["lon"]),
                    (res["body"]["southWest"]["lat"], res["body"]["southWest"]["lon"]),
                ]
                poly = Polygon(coords)

                boats = []
                for boat in boats_all:
                    p = Point(boat[2].latitude, boat[2].longitude)

                    if poly.contains(p):
                        if boat not in boats:
                            boats.append(boat)
                    else:
                        if boat in boats:
                            index = boats.index(boat)
                            boats.pop(index)

                data = {
                    "header": "boatsOnMap",
                    "body": {
                        "boats": [
                            {
                                "id": boat[0].id,
                                "name": boat[0].name,
                                "rating": boat[0].boat_raiting,
                                "images": [
                                    i.image for i in crud.get_images(db, boat[0].id)
                                ],
                                "cost": int(boat[0].cost),
                                "captain": {
                                    "name": boat[1].name,
                                    "rating": boat[1].raiting,
                                },
                                "coordinates": {
                                    "lat": boat[2].latitude,
                                    "lon": boat[2].longitude,
                                },
                                "piers": [p.id for p in crud.get_piers(db, boat[0].id)],
                            }
                            for boat in boats
                        ]
                    },
                }

                await client_manager.send_personal_message(data, client.phone)

            if res["header"] == "stopBoatsOnArea":
                print("Остановить поиск лодок")
                # background_tasks.add_task(
                #     send_notification, client.phone, res["body"]["orderId"], db
                # )

            if res["header"] == "startOrderProcessing":
                # background_tasks.add_task(
                #     send_notification, client.phone, res["body"]["orderId"], db
                # )
                await send_notification(client.phone, res["body"]["orderId"], db)
                # order = crud.get_order_by_id(db, res["body"]["orderId"])
                # coord = crud.get_boat_coordinates(db, order.boat_id)
                # data = {
                #     "header": "currentOrderInfo",
                #     "body": {
                #         "orderId": res["body"]["orderId"],
                #         "boatCoordinates": {
                #             "lat": coord.latitude,
                #             "lon": coord.longitude,
                #         },
                #         "boatId": order.boat_id,
                #         "pierId": order.pier_id,
                #         "approximateArrivalTime": "30:05",
                #     },
                # }
                # await client_manager.send_personal_message(data, client.phone)

    except WebSocketDisconnect:
        client_manager.disconnect(client.phone)


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
        "cost": int(boat.cost),
        "captain": {"name": captain.name, "rating": captain.raiting},
        "length": boat.length,
        "power": boat.power,
        "capacity": boat.capacity,
    }

    return result


@router.post("/order/client/create", tags=["customer"], status_code=201)
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

    await captain_manager.send_personal_message(data, captain.phone)
    # await client_manager.send_personal_message()
    return {"orderId": order.id}


@router.post(
    "/order/client/reject",
    status_code=201,
    dependencies=[Depends(get_user_from_header)],
    tags=["customer"],
)
async def client_reject(order_id: schemas.Id, db: Session = Depends(get_db)):

    crud.set_customer_reject(db, order_id.orderId)

    data = {"header": "ClientOrderRejected", "body": {"orderId": order_id.orderId}}
    order = crud.get_order_by_id(db, order_id.orderId)
    boat = crud.get_boat_by_id(db, order.boat_id)
    captain = crud.get_captain(db, boat.captain_id)
    await captain_manager.send_personal_message(data, captain.phone)


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
    "/piers",
    tags=["customer"],
    status_code=201,
    dependencies=[Depends(get_user_from_header)],
)
async def get_pier(
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
        "piers": piers_list,
    }
