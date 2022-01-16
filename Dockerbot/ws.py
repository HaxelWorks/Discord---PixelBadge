import asyncio
import websockets

async def consumer_handler(websocket):
    async for message in websocket:
        await consumer(message)
        
async def producer_handler(websocket):
    while True:
        message = await producer()
        await websocket.send(message)
    
    
async def handler(websocket):
    await asyncio.gather(
        consumer_handler(websocket),
        producer_handler(websocket),
    )

async def handler(websocket):
    consumer_task = asyncio.create_task(consumer_handler(websocket))
    producer_task = asyncio.create_task(producer_handler(websocket))
    done, pending = await asyncio.wait(
        [consumer_task, producer_task],
        return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
        task.cancel()
        


connected = set()

async def handler(websocket):
    # Register.
    connected.add(websocket)
    try:
        # Broadcast a message to all connected clients.
        websockets.broadcast(connected, "Hello!")
        await asyncio.sleep(10)
    finally:
        # Unregister.
        connected.remove(websocket)