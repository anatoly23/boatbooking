from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src import crud, schemas
from src.core.dependencies import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_db,
)

router = APIRouter()


@router.post("/register")
async def register(captain: schemas.Captain, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_phone(db, phone=captain.phone)
    if db_user:
        raise HTTPException(status_code=201, detail="Sucess")
    raise HTTPException(status_code=400, detail="Acess denied")


@router.post(
    "/login", response_model=schemas.Token, status_code=status.HTTP_201_CREATED
)
async def login(captain: schemas.AuthenticationMobile, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_phone(db, phone=captain.phone)
    if not db_user:
        raise HTTPException(status_code=400, detail="Acess denied")
    if captain.code != "0":
        raise HTTPException(status_code=401, detail="Auth problem")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        {"phone": captain.phone, "code": captain.code},
        expires_delta=access_token_expires,
    )
    return schemas.Token(
        access_token=access_token, refresh_token=access_token, ws_token=access_token
    )
