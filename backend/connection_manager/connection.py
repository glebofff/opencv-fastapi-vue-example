import asyncio
from fastapi import WebSocket

class Connection:
    def __init__(self, ws: WebSocket, device_id: int = 0):
        self.ws = ws
        self.device_id = device_id

    async def ensure_alive(self, timeout=1.0):
        try:
            await asyncio.wait_for(self.ws.receive_bytes(), timeout=timeout)
        except asyncio.TimeoutError:
            pass
