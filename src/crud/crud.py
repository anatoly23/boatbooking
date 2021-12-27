from sqlalchemy.orm import Session
from src import models, schemas


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(phone=user.phone)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_phone(db: Session, phone: str):
    return db.query(models.User).filter(models.User.phone == phone).first()
