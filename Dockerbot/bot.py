import discord
import asyncio
import http
import websockets
from tokens import TOKEN
from util import id_generator
from collections import defaultdict

HOST_IP = "192.168.0.147"

# DISCORD PART
routing_table = defaultdict(lambda: None)  # Routes guild_ids to websockets
pending_sockets = defaultdict(lambda: None)  #


class DiscordClient(discord.Bot):
    # This is here for debugging purposes
    async def on_ready(self):
        print("Logged on as {0}!".format(self.user))

    # This is here for debugging purposes
    async def on_message(self, message):
        print("Message from {0.author}: {0.content}".format(message))

    # Triggers whenever a user enters or leaves a voice channel
    async def on_voice_state_update(self, user, before, after):
        # If the user has joined a voice channel
        if before.channel is None and after.channel is not None:
            state = "joined"
            channel = after.channel
            
        # If the user has left a voice channel
        elif before.channel is not None and after.channel is None:
            state = "left"
            channel = before.channel

        
        message = f"{user} has {state} {channel.name}"
        print(message)

        # Check if there are receiving sockets for this guild
        if (sockets := routing_table[channel.guild.id]) is not None:
            # If there are, send the websockets a message
            coros = [sock.send(message) for sock in sockets]
            await asyncio.gather(*coros)


bot = DiscordClient(sync_commands=False)


@bot.slash_command()
async def connect_ipane(ctx, key: str):
    if websocket := pending_sockets[key]:
        if (
            routing_table[ctx.guild.id] is None
        ):  # If there are no sockets for this guild
            routing_table[ctx.guild.id] = [
                websocket
            ]  # Add the socket to the routing table in a list
        else:
            routing_table[ctx.guild.id].append(websocket)

        await websocket.send("connection_accepted")
        await ctx.respond("Connection accepted")
        pending_sockets.pop(key)
        print(f"{ctx.author}'s Ipane is connected to {ctx.guild.name}")
    else:
        await ctx.respond("key not found")


# WEBSOCKET PART
async def health_check(path, request_headers):
    if path == "/healthz":
        return http.HTTPStatus.OK, [], b"OK\n"


async def receive_ws(websocket):

    async for message in websocket:
        if message.startswith("connect"):
            key = message.split(":")[1]
            print(f"key: {key} wants to connect")
            pending_sockets[key] = websocket
        await websocket.send("connection_pending")

# TODO implement a health check for the connected ipanes


async def ws_server_run():
    async with websockets.serve(
        receive_ws,
        HOST_IP,
        8765,
        process_request=health_check,
    ):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    asyncio.gather(ws_server_run(), bot.start(TOKEN))
    loop.run_forever()
