import datetime
from sqlalchemy import func

from sqlalchemy.orm import Session
from src import models, schemas


def create_user(db: Session, user: schemas.Captain):
    db_user = models.Captain(phone=user.phone)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_phone(db: Session, phone: str):
    return db.query(models.Captain).filter(models.Captain.phone == phone).first()


def get_boat(db: Session, capitan_id: int):
    boat = (
        db.query(models.Boat)
        .join(models.Captain)
        .filter(models.Captain.id == capitan_id)
        .one()
    )
    return boat


def get_captain(db: Session, id):
    return db.query(models.Captain).filter(models.Captain.id == id).first()


def get_boat_by_id(db: Session, id: int):
    boat = db.query(models.Boat).filter(models.Boat.id == id).first()
    return boat


def get_images(db: Session, boat_id: int):
    images = db.query(models.Image).filter(models.Image.boat_id == boat_id).all()
    return images


def get_piers(db: Session, boat_id: int):
    piers = db.query(models.Pier).filter(models.Pier.boat_id == boat_id).all()
    return piers


def get_piers_all(db: Session):
    return db.query(models.Pier)


def get_pier(db: Session, pier_id: int):
    pier = db.query(models.Pier).filter(models.Pier.id == pier_id).first()
    return pier


def get_pier_images(db: Session, pier_id: int):
    images = db.query(models.Image).filter(models.Image.boat_id == pier_id).all()
    return images


def get_order(db: Session, boat_id: int):
    order = (
        db.query(models.Order)
        .join(models.Boat)
        .order_by(models.Order.time_created.desc())
        .filter(models.Boat.id == boat_id)
        .filter(models.Order.order_state == 0)
        .first()
    )
    return order


def get_current_order(db: Session, client_id):
    order = (
        db.query(models.Order)
        .filter(models.Order.client_id == client_id)
        .filter(models.Order.order_state == 0)
        .one()
    )
    return order


def get_order_by_id(db: Session, orderId):
    order = db.query(models.Order).filter(models.Order.id == orderId).one()
    return order


# def get_client_order(db: Session, client_id):
#     return (
#         db.query(models.Order)
#         .filter(models.Order.client_id == client_id)
#         .order_by(models.Order.time_created)
#         .all()
#     )


def set_order(
    db: Session,
    comment: str,
    client_id: int,
    pier_id: int,
    boat_id: int,
    minTimeOrder: int,
):
    order = models.Order(
        comment=comment,
        time_created=datetime.datetime.now(),
        order_state=0,
        minTimeOrder=minTimeOrder,
        client_id=client_id,
        boat_id=boat_id,
        pier_id=pier_id,
    )
    db.add(order)
    db.commit()
    return order


def set_customer_reject(db: Session, id: int):
    db.query(models.Order).filter(models.Order.id == id).update({"order_state": 4})
    db.commit


def set_captain_accept(db: Session, id: int):
    db.query(models.Order).filter(models.Order.id == id).update({"order_state": 1})
    db.commit()


def set_capitan_complete(db: Session, id: int):
    db.query(models.Order).filter(models.Order.id == id).update({"order_state": 2})
    db.commit()


def set_captain_reject(db: Session, id: int):
    db.query(models.Order).filter(models.Order.id == id).update({"order_state": 3})
    db.commit()


def set_boat_coordinate(
    db: Session, longitude: float, latitude: float, state: int, boat_id: int
):
    db.query(models.BoatCoordinate).filter(
        models.BoatCoordinate.boat_id == boat_id
    ).update(
        {
            "longitude": longitude,
            "latitude": latitude,
            "state": state,
            "boat_id": boat_id,
        },
    )
    db.commit()


def get_boat_coordinates(db: Session, boat_id):
    return (
        db.query(models.BoatCoordinate)
        .filter(models.BoatCoordinate.boat_id == boat_id)
        .one()
    )


def create_client(db: Session, phone: schemas.Client):
    db_user = models.Client(phone=phone)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)


def get_client(db: Session, phone: str):
    client = db.query(models.Client).filter(models.Client.phone == phone).first()
    return client


def get_client_by_id(db: Session, client_id: int):
    client = (
        db.query(models.Client)
        .join(models.Order)
        .order_by(models.Order.time_created.desc())
        .filter(models.Client.id == client_id)
        .first()
    )
    return client


def get_ordedrs_by_date(db: Session, client_id: int):
    return (
        db.query(models.Order.id, func.date(models.Order.time_created))
        .filter(models.Order.client_id == client_id)
        .group_by(func.date(models.Order.time_created))
        .all()
    )


def get_orders_by_time(db, client_id: int, date: str):
    orders = (
        db.query(models.Order, models.Boat, models.Captain)
        .join(models.Boat, models.Boat.id == models.Order.boat_id)
        .join(models.Captain, models.Captain.id == models.Boat.captain_id)
        .filter(func.date(models.Order.time_created) == date and client_id == client_id)
        .all()
    )

    return orders
