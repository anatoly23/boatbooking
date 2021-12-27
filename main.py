
import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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


@app.post("/register", response_model=schemas.User)
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_phone(db, phone=user.phone)
    if db_user:
        raise HTTPException(status_code = 400, detail =  "Acess denied")
    else:
        crud.create_user(db=db, user=user)
        raise HTTPException(status_code = 201, detail =  "Sucess")


@app.post("/login", response_model=schemas.Token)
async def login(user: schemas.AuthenticationMobile, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_phone(db, phone=user.phone)
    if not db_user:
        raise HTTPException(status_code = 400, detail =  "Acess denied")
    if user.code != '0000':
        raise HTTPException(status_code = 401, detail =  "Auth problem")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        {'phone': user.phone, 'code': user.code}, expires_delta=access_token_expires
    )
    return {
            "access_token": access_token,
            "refresh_token": access_token,
            "ws_token": access_token
                }


@app.post("/order/captain/reject")
async def capitan_appointment():
    return {"message": "Hello World"}


@app.get("/captain/appointment")
async def capitan_appointment():
    return {"message": "Hello World"}


@app.post("/order/captain/complete")
async def capitan_complete():
    return {"message": "Hello World"}


@app.post("/order/captain/accepted")
async def capitan_accepted():
    return {"message": "Hello World"}


@app.get("/order/captain/current")
async def capitan_current():
    return {"message": "Hello World"}
