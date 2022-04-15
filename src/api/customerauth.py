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


@router.post("/client/register", tags=["customer"])
async def register(client: schemas.Client, db: Session = Depends(get_db)):
    db_user = crud.get_client(db, phone=client.phone)
    if db_user:
        raise HTTPException(status_code=201, detail="Sucess")
    else:
        crud.create_client(db, client.phone)
        raise HTTPException(status_code=201, detail="Sucess")
    raise HTTPException(status_code=400, detail="Acess denied")


@router.post(
    "/client/login",
    response_model=schemas.Token,
    status_code=status.HTTP_201_CREATED,
    tags=["customer"],
)
async def login(client: schemas.AuthenticationMobile, db: Session = Depends(get_db)):
    db_user = crud.get_client(db, phone=client.phone)
    if not db_user:
        raise HTTPException(status_code=400, detail="Acess denied")
    if client.code != "0":
        raise HTTPException(status_code=401, detail="Auth problem")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        {"phone": client.phone, "code": client.code},
        expires_delta=access_token_expires,
    )
    return schemas.Token(
        access_token=access_token, refresh_token=access_token, ws_token=access_token
    )
