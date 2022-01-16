import discord
import asyncio
import http
import websockets
from tokens import TOKEN



class MyClient(discord.Client):
    # This is here for debugging purposes
    async def on_ready(self):
        print("Logged on as {0}!".format(self.user))

    # This is here for debugging purposes
    async def on_message(self, message):
        print("Message from {0.author}: {0.content}".format(message))

    # Triggers whenever a user enters or leaves a voice channel
    async def on_voice_state_update(self, user, before, after):
        if after.channel is None:
            print(user.name + " left channel ", before.channel) 
        else:           
            print(user.name + " has joined " + after.channel.name)
        
        


client = MyClient()




async def health_check(path, request_headers):
    if path == "/healthz":
        return http.HTTPStatus.OK, [], b"OK\n"


async def echo(websocket):
    async for message in websocket:
        await websocket.send(message)


async def run_websock():
    async with websockets.serve(
        echo,
        "localhost",
        8765,
        process_request=health_check,
    ):
        await asyncio.Future() # run forever

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    asyncio.gather(run_websock(), client.start(TOKEN))
    loop.run_forever()

