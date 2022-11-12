import json
import asyncio
import websockets

async def hello():
    async with websockets.connect("ws://localhost:8000/ws/chat/?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE2NjMwMDk0ODEsInN1YiI6ImFjY2VzcyJ9.26g6zeqq8qzZzjmhEUhvt8yH1G4UI2ZD4CeG48ShSJg") as websocket:
        await websocket.send(json.dumps({
            'pk': "3",
            'action': "join_room",
            'request_id': 123,
        }))
        await websocket.send(json.dumps({
            'pk': "3",
            'action': "rdetrieve",
            'request_id': 123,
        }))
        await websocket.send(json.dumps({
            'pk': "3",
            'action': "subscribe_to_messages_in_room",
            'request_id': 123,
        }))
        await websocket.send(json.dumps({
            'pk': "3",
            'action': "subscribe_instance",
            'request_id': 123,
        }))
        while True:
            w = await websocket.recv()
            print(w)

TOKEN = "s"
TOKEN = "0d2fbbd2e568294cd3b95471388275e300e51a93"

async def test_MessageConsumer():
    async with websockets.connect("ws://localhost:8000/ws/messages/?token=" + TOKEN) as websocket:
        await websocket.send(json.dumps({
            'pk': "3",
            'action': "start_listen",
            'request_id': 123,
        }))
        while True:
            w = await websocket.recv()
            print(w)


async def create_message():
    async with websockets.connect("ws://localhost:8000/ws/messages/?token=" + TOKEN) as websocket:
        await websocket.send(json.dumps({
            'action': "create_message",
            'chat_id': 1,
            'text': "Это всё работает123123123",
            'request_id': 123,
        }))
        while True:
            w = await websocket.recv()
            print(w)

asyncio.run(create_message())
