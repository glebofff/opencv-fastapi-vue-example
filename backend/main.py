import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi_utils.tasks import repeat_every
from connection_manager import ConnectionManager
from capturer import Capturer

app = FastAPI()
manager = ConnectionManager()
cap = Capturer()

@app.on_event('startup')
@repeat_every(seconds=5)
async def take_picture():
    devices = list(manager.device_ids)
    cap.refresh_devices(devices)
    if not manager.connections:
        return

    for device_id in manager.device_ids:
        image = cap.get_image(device_id)
        if image is None:
            continue
        await manager.broadcast_bytes(image, device_id=device_id)



@app.websocket('/ws/{device}', 'websocket')
async def websocket_endpoint(websocket: WebSocket, device: int=0):
    connection = await manager.connect(websocket=websocket, device_id=device)
    try:
        while True:
            await connection.ensure_alive(timeout=0.5)
            await asyncio.sleep(0.5)

    except WebSocketDisconnect:
        manager.disconnect(connection=connection)
