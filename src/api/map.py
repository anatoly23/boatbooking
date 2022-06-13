from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from src.core.manager import boatmanager

templates = Jinja2Templates(directory="src/templates")

router = APIRouter()


@router.get("/map", response_class=HTMLResponse, tags=["map"])
async def map(request: Request):
    return templates.TemplateResponse("map.html", {"request": request})


@router.websocket("/ws/wscoords")
async def coords_endpoit(websocket: WebSocket):
    await boatmanager.connect(websocket)
    try:
        while True:
            res = await websocket.receive_json()
            print(res)

    except WebSocketDisconnect:
        boatmanager.disconnect(websocket)
