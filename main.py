import os
from datetime import datetime, timedelta
from typing import Optional

import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.security.utils import get_authorization_scheme_param
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

import settings
from src import crud, schemas
from src.db.database import SessionLocal, create_db

create_db()

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user_from_header(*, authorization: str = Header(None)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    scheme, token = get_authorization_scheme_param(authorization)
    if scheme.lower() != "bearer":
        raise credentials_exception
    try:
        payload = jwt.decode(
            token, SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        try:
            token_data = schemas.Captain(**payload)
            return token_data
        except ValidationError:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception


@app.post("/register")
async def register(captain: schemas.Captain, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_phone(db, phone=captain.phone)
    if db_user:
        raise HTTPException(status_code=201, detail="Sucess")
    raise HTTPException(status_code=400, detail="Acess denied")


@app.post("/login", response_model=schemas.Token, status_code=status.HTTP_201_CREATED)
async def login(captain: schemas.AuthenticationMobile, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_phone(db, phone=captain.phone)
    if not db_user:
        raise HTTPException(status_code=400, detail="Acess denied")
    if captain.code != '0':
        raise HTTPException(status_code=401, detail="Auth problem")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        {'phone': captain.phone, 'code': captain.code}, expires_delta=access_token_expires
    )
    return schemas.Token(access_token=access_token, refresh_token=access_token, ws_token=access_token)


@app.post("/order/captain/reject")
async def capitan_reject():
    return {"message": "Hello World"}


@app.get("/captain/appointment", response_model=schemas.Boat)
async def capitan_appointment(captain: schemas.Captain = Depends(get_user_from_header), db: Session = Depends(get_db)):
    capitan = crud.get_user_by_phone(db, captain.phone)
    boat = crud.get_boat(db, capitan.id)
    images = crud.get_images(db, boat.id)
    image_list = [i.image for i in images]
    piers = crud.get_piers(db, boat.id)

    piers_list = [
        schemas.Pier(id=pier.id, name=pier.name, coordinates=schemas.Coordinates(lat=pier.lat, lon=pier.lon))
        for pier in piers
    ]

    results = schemas.Boat(id=boat.id, name=boat.name, boat_rating=boat.boat_raiting,
                           captian_rating=capitan.raiting, images=image_list, cost=boat.cost, piers=piers_list)
    return results


@app.post("/order/captain/complete")
async def capitan_complete():
    return {"message": "Hello World"}


@app.post("/order/captain/accepted")
async def capitan_accepted():
    return {"message": "Hello World"}


@app.get("/order/captain/current", response_model=schemas.Order)
async def capitan_current(captain: schemas.Captain = Depends(get_user_from_header), db: Session = Depends(get_db)):
    capitan = crud.get_user_by_phone(db, captain.phone)
    boat = crud.get_boat(db, capitan.id)
    order = crud.get_order(db, boat.id)
    client = crud.get_client(db, order.id)

    return schemas.Order(orderId=order.id,
                         boatId=order.boat_id,
                         pierId=order.pier_id,
                         clientPhone=client.phone,
                         comment=order.comment,
                         timeCreated=str(order.time_created),
                         orderState=order.order_state,
                         minTimeOrder=order.minTimeOrder)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
