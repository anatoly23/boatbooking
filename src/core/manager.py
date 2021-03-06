from src import schemas
from typing import Dict, List
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, phone: schemas.Captain):
        await websocket.accept()
        if phone in self.active_connections:
            self.disconnect(phone)
        self.active_connections[phone] = websocket
        # print(f"{phone} подключился. WS: {self.active_connections[phone]}")

    def disconnect(self, phone: schemas.Captain):
        # print(f"{phone} отключился. WS: {self.active_connections[phone]}")
        if phone in self.active_connections:
            self.active_connections.pop(phone)

    async def send_personal_message(self, message: str, phone: schemas.Captain):
        await self.active_connections[phone].send_json(message)

    async def broadcast(self, message: str):
        for _, connection in self.active_connections.items():
            print("send the message")
            await connection.send_json(message)

    async def list_ws(self):
        # for phone, connection in self.active_connections.items():
        #     print(f"{phone}, подключение {connection}")
        print(self.active_connections)


class BoatManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_json(message)

    async def list_ws(self):
        for connection in self.active_connections:
            print(f"соединение: {connection}")


captain_manager = ConnectionManager()
client_manager = ConnectionManager()
boatmanager = BoatManager()
