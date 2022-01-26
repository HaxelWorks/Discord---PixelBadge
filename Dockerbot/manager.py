"""
Connection manager has multiple functions

1: Holds websocket connection to a badge
2: It pings this connection periodically for availability,
3: removes connection if it does not respond,
4: remembers previous connections, and reconnects them
6: can change the color,brigtness and timezone of the Ipane
"""
import asyncio
from collections import defaultdict
import discord
import websockets
from os import path
import pickle
import atexit

from util import LOGGER

class Conns:
    """
    Contains all the connections.
    This class does not need to be instantiated.

    """
    
    pending = defaultdict(lambda: None)  # key: key, value: websocket
    routing = defaultdict(lambda: None)  # guild_id -> [BadgeUser]
    users = defaultdict(lambda: None)  # key: UserId, value: BadgeUser
    known_keys = defaultdict(lambda: None)  # key: key, value: BadgeUser

CONNS_PATH = "connections.p"
# if the file exists, load the connections
if path.exists(CONNS_PATH):
    LOGGER.info("Loading previous connections")
    Conns = pickle.load(open(CONNS_PATH, "rb"))


def save_connections() -> None:
    """Save the connections to a file by pickling the Conns class"""
    print("Saving connections")
    pickle.dump(Conns, open(CONNS_PATH, "wb"))
    print("Saved connections")


atexit.register(save_connections)


class BadgeUser:
    """Ties badges websockets to a user, and a guild."""

    def __init__(self, websocket, key: str, user: discord.User, guild: discord.Guild):
        self.websockets = {key: websocket}  # there can be multiple websockets
        self.guild = guild  # this is the inital guild, the connection can be assigned to multiple guilds in the routing table
        self.user = user

    @property
    def active(self):
        return bool(self.websockets)

    async def _try_send(self, key: str, websocket, message: str):
        """Tries to send a message to a websocket. if it fails, it removes the websocket from the list of active websockets"""
        try:
            await websocket.send(message)
        except:
            LOGGER.error(f"{self.user}'s connection {key} is has been lost")
            self.websockets.pop(key)

    async def send_to_badges(self, message: str):
        """send message to all badges connected to this user"""
        if self.active:  # if there are active websockets
            await asyncio.gather(
                *[
                    self._try_send(key, websocket, message)
                    for key, websocket in self.websockets.items()
                ]
            )


class SlashCommands:
    """This class does not need to be instantiated."""

    @staticmethod
    async def connect_badge(ctx, key: str):
        """Connect a badge to your user account"""

        user = ctx.author
        guild = ctx.guild

        key = key.upper()
        if not (
            ws := Conns.pending[key]
        ):  # If the key is invalid, do nothing and return
            await ctx.send("Invalid key")
            return

        if not (badge_user := Conns.users[user.id]):  # If the user has no badges
            badge_user = Conns.users[user.id] = BadgeUser(
                ws, key, user, guild
            )  # create a new badge user
            LOGGER.info(f"new badge user: {user.name}")
        else:  # If the user already has a badge connected
            badge_user.websockets[
                key
            ] = ws  # use the key to connect the websocket to the badge user
            LOGGER.info(f"new badge connected to user: {user.name}")

        # Add the user to the routing table
        if routes := Conns.routing[guild.id]:  # if the guild has a routing table
            routes.append(badge_user)
        else:  # if the guild has no routing table
            Conns.routing[guild.id] = [badge_user]
        
        # add the key to the keys table
        Conns.known_keys[key] = badge_user    

        # Acknoledge the connection
        msg = "connection accepted"
        await asyncio.gather(ws.send(msg), ctx.respond(msg))
        LOGGER.info(f"{user}'s Ipane is connected to {guild.name}")

        # Clean up the pending connections
        Conns.pending.pop(key)

    @staticmethod
    async def enable_notifications(ctx):
        """Enable notifications for this server"""

        if not (badge_user := Conns.users[ctx.author.id]):  # If the user has no badges
            await ctx.respond("You have no badge connected")
            return

        if table := Conns.routing[ctx.guild.id]:  # if the guild has a routing table
            table.append(badge_user)
        else:  # if the guild has no routing table
            Conns.routing[ctx.guild.id] = [badge_user]
        await ctx.respond("Enabled")
        LOGGER.info(f"{ctx.author}'s Badges are enabled on {ctx.guild.name}")


from util import key_generator

# This is a callback function used by the websocket server


async def receive_new_websocket(websocket: websockets.WebSocketServerProtocol) -> None:
    """Receive a new websocket connection and add it to the pending connections table"""
    try:
        async for message in websocket:
            if message == "connect":
                key = key_generator(7)
                Conns.pending[key] = websocket
                LOGGER.info(f"key: {key} wants to connect")
                await websocket.send("connection waiting:" + key)

            elif message.startswith("reconnect"):
                await websocket.send("connection waiting")
                key = message.split(":")[1]
                # if the key is found
                if badge_user := Conns.known_keys[key]:
                    badge_user.websockets[key] = websocket
                    await websocket.send("connection accepted")
                    LOGGER.info(f"key: {key} reconnected")
                else:
                    await websocket.send("connection denied")
                    LOGGER.info(f"key: {key} reconnected but key is invalid")
                
                
    except:
        LOGGER.error(f"{websocket} has been lost")
