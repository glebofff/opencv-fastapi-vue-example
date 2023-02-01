import asyncio
from fastapi import WebSocket
from .connection import Connection


class ConnectionManager:
    def __init__(self):
        self.connections: list[Connection] = []

    @property
    def device_ids(self):
        return set([c.device_id for c in self.connections])

    async def connect(self, websocket: WebSocket, device_id: int = 0):
        await websocket.accept()
        connection = Connection(ws=websocket, device_id=device_id)
        self.connections.append(connection)
        return connection

    def disconnect(self, connection: Connection):
        self.connections.remove(connection)

    async def broadcast_bytes(self, data: bytes, device_id: int = 0):
        aws = [
            con.ws.send_bytes(data) for con in self.connections if con.device_id == device_id
        ]
        await asyncio.wait(aws)