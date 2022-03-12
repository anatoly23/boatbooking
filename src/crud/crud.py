import datetime

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
    boat = db.query(models.Boat).join(models.Captain).filter(models.Captain.id == capitan_id).one()
    return boat


def get_images(db: Session, boat_id: int):
    images = db.query(models.Image).filter(models.Image.boat_id == boat_id).all()
    return images


def get_piers(db: Session, boat_id: int):
    piers = db.query(models.Pier).filter(models.Pier.boat_id == boat_id).all()
    return piers


def get_order(db: Session, boat_id: int):
    order = db.query(models.Order).join(models.Boat).order_by(models.Order.time_created.desc()).filter(models.Boat.id == boat_id).filter(models.Order.order_state == 0).first()
    return order


def get_client_by_id(db: Session, client_id: int):
    client = db.query(models.Client).join(models.Order).order_by(models.Order.time_created.desc()).filter(models.Client.id == client_id).first()
    return client


def get_client(db: Session, phone: str):
    client = db.query(models.Client).filter(models.Client.phone == phone).one()
    return client


def set_order(db: Session, comment: str, client_id: int, pier_id: int, boat_id: int):
    order1 = models.Order(comment=comment, time_created=datetime.datetime.now(), order_state=0, minTimeOrder=10, client_id=client_id, boat_id=boat_id, pier_id=pier_id)
    db.add(order1)
    db.commit()


def set_captain_accept(db: Session, id: int):
    db.query(models.Order).filter(models.Order.id == id).update({'order_state': 1})
    db.commit()


def set_capitan_complete(db: Session, id: int):
    db.query(models.Order).filter(models.Order.id == id).update({'order_state': 2})
    db.commit()
