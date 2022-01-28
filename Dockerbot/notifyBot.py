import asyncio
import http
import websockets
from tokens import TOKEN
from collections import defaultdict
import time
import math
import manager
import discord


HOST_IP = "192.168.0.147"


# DISCORD PART
class DiscordClient(discord.Bot):
    # This is here for debugging purposes
    async def on_ready(self):
        print("Logged on as {0}!".format(self.user))

    # This is here for debugging purposes
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

        # If the user has left a voice channel
        elif before.channel is not None and after.channel is None:
            state = "left"
            channel = before.channel

        # If the user has moved to a different voice channel
        elif before.channel != after.channel:
            state = "moved to"
            channel = after.channel
        else:  # Do nothing and return
            return

        # Remove the hashtag from the user id
        user = user.name.split("#")[0]
        print(message := f"{user}:{state}:{channel.guild.name}:{channel.name}")
        if badge_users := manager.ConnStore.routing[channel.guild.id]:
            await asyncio.gather(*[bu.send_to_badges(message) for bu in badge_users])


# The manager is imported after creation of the bot
# This is because the manager needs the bot to register the slash command
bot = DiscordClient()


# add the slash commands from the manager to the bot
@bot.slash_command()
async def connect_badge(ctx, key: str):
    """Connects a badge to a user"""
    await manager.SlashCommands.connect_badge(ctx=ctx, key=key)


@bot.slash_command()
async def enable_notifications(ctx):
    """Enables notifications for the current server"""
    await manager.SlashCommands.enable_notifications(ctx=ctx)


# WEBSOCKET PART
async def health_check(path, request_headers):
    if path == "/healthz":
        return http.HTTPStatus.OK, [], b"OK\n"


async def socket_server_run():
    print("Starting websocket server")   
    async with websockets.serve(
        manager.receive_new_websocket,
        HOST_IP,
        8765,
        process_request=health_check,
    ):
        await asyncio.Future()  # run forever
async def restart(coro):
    while True:
        try:
            await coro()
        except Exception as e:
            print(f"Restarting due to {e}")
            

            
        
    


async def keepalive():
    print("Starting keepalive")
    while True:
        # sleep until the next whole minute
        now = time.time()
        await asyncio.sleep(60 * (math.ceil(now / 60) - now / 60))

        # execute the keepalive command on all active sockets
        active_users = [usr for usr in manager.ConnStore.users.values() if usr.active]
        if active_users:
            await asyncio.gather(*[usr.send_to_badges("ping") for usr in active_users])          
        else:
            print("No active sockets")


def main():
    loop = (
        asyncio.get_event_loop()
    )  # INVESTIGATE "DeprecationWarning: There is no current event loop"
    asyncio.set_event_loop(loop)
    loop.create_task(bot.start(TOKEN))
    loop.create_task(restart(socket_server_run))
    loop.create_task(keepalive())
    loop.run_forever()


if __name__ == "__main__":
    main()
