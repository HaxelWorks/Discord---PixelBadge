import asyncio
import http
import websockets
from tokens import TOKEN
from collections import defaultdict
import time
import math
import manager
import discord
from util import Colors, rgb_to_hex

# import threading


HOST_IP = "192.168.0.147"
PORT = 8765

# DISCORD PART
class DiscordClient(discord.Bot):
    # This is here for debugging purposes
    async def on_ready(self):
        print("Logged on as {0}!".format(self.user))

    # This is here for future purposes
    # async def on_message(self, message):
    #     print("Message from {0.author}: {0.content}".format(message))
    #     if message.content == "sync_commands":
    #         print("sync commands")
    #         await self.register_commands()

    # Triggers whenever a user enters or leaves a voice channel
    async def on_voice_state_update(self, user: discord.User, before, after):

        # If the user has joined a voice channel
        if before.channel is None and after.channel is not None:
            state = "joined"
            channel = after.channel
            color = Colors.GREEN

        # If the user has left a voice channel
        elif before.channel is not None and after.channel is None:
            state = "left"
            channel = before.channel
            color = Colors.RED

        # If the user has moved to a different voice channel
        elif before.channel != after.channel:
            state = "moved to"
            channel = after.channel
            color = Colors.ORANGE
        else:  # Do nothing and return
            return

        # Remove the hashtag from the user id
        user = user.name.split("#")[0]

        print(
            message := f"{user} {state} {channel.guild.name} {channel.name}{rgb_to_hex(color)}"
        )
        await manager.Conns.send_by_guild(channel.guild.id, message)


BOT = DiscordClient()


# add the slash commands from the manager to the bot
@BOT.slash_command()
async def connect_badge(ctx, key: str):
    """Connects a badge to your user id"""
    await manager.SlashCommands.connect_badge(ctx=ctx, key=key)


@BOT.slash_command()
async def enable_notifications(ctx):
    """Enables notifications for the current server"""
    await manager.SlashCommands.enable_notifications(ctx=ctx)


# WEBSOCKET PART
async def health_check(path, request_headers):
    if path == "/healthz":
        return http.HTTPStatus.OK, [], b"OK\n"
    print("Starting websocket server")


def never():
    """ this is an async trick to keep the event loop alive """
    try:
        return never.never
    except AttributeError:
        never.never = asyncio.Future()
        return never.never


async def socket_server_run():
    async with websockets.serve(
        manager.receive_new_websocket,
        HOST_IP,
        PORT,
        process_request=health_check,
    ):
        await never()  # Never ends


async def restart(coro):
    while True:
        try:
            await coro()
        except Exception as e:
            print(f"Restarting due to {e}")
            await asyncio.sleep(5)


async def keepalive(interval=30):
    print("Starting keepalive")
    while True:
        # sleep until the next whole minute
        now = time.time()
        await asyncio.sleep(interval * (math.ceil(now / interval) - now / interval))
        #prints ping and a formatted time
        print(f"Ping: {time.strftime('%H:%M:%S')}")
        # send a ping to all connected badges
        await manager.Conns.send_broadcast("ping")


def main():
    loop = asyncio.get_event_loop()
    # INVESTIGATE "DeprecationWarning: There is no current event loop"
    asyncio.set_event_loop(loop)

    loop.create_task(BOT.start(TOKEN))
    loop.create_task(socket_server_run())
    loop.create_task(keepalive())
    loop.run_forever()


if __name__ == "__main__":
    main()
