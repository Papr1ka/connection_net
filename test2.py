import json
import asyncio
import websockets


TOKEN = "8057a0025f863fffe6fabe4e192a5aab417bfe92"

async def test_MessageConsumer():
    async with websockets.connect("ws://localhost:8000/ws/messages/?token=" + TOKEN) as websocket:
        await websocket.send(json.dumps({
            'pk': "3",
            'action': "start_listen",
            'request_id': 22,
        }))
        await websocket.send(json.dumps({
            'pk': "3",
            'action': "subscribe_instance",
            'request_id': 22,
        }))
        
        while True:
            w = await websocket.recv()
            print(w)


asyncio.run(test_MessageConsumer())
