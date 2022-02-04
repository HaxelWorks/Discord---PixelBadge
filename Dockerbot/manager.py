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
import yaml
import atexit
from types import SimpleNamespace

class Conns(SimpleNamespace):
    """
    Contains all the connections to badges
    This class does not need to be instantiated.
    """

    pending = defaultdict(lambda: None)  #   key: key, value: websocket
    keyuser = defaultdict(lambda: None)  #   key: key, value: user_id
    routing = defaultdict(lambda: None)  #   key: guild_id, value: [user_id]
    sockcon = defaultdict(lambda: None)  #   key: user_id, value: [websocket]
    # in order to turn guild_id into the target websockets, we do this:
    # routing[guild_id] --> [user_id] --> sockcon[user_id] --> [websocket]

    # we pack and unpack into yaml files
    @classmethod
    def pack(cls):
        """
        Packs the class into a yaml file
        """
        with open(
            path.join(path.dirname(path.abspath(__file__)), "badges.yaml"), "w"
        ) as f:
            yaml.dump(
                {
                    "pending": cls.pending,
                    "keyuser": cls.keyuser,
                    "routing": cls.routing,
                    "sockcon": cls.sockcon,
                },
                f,
            )

    @classmethod
    def unpack(cls):
        """
        Unpacks the class from a yaml file
        """
        with open(
            path.join(path.dirname(path.abspath(__file__)), "badges.yaml"), "r"
        ) as f:
            data = yaml.load(f)
            # TODO can this be done using setattr?
            cls.pending = data["pending"]
            cls.keyuser = data["keyuser"]
            cls.routing = data["routing"]
            cls.sockcon = data["sockcon"]

    @classmethod
    async def _try_send(cls, websocket, message: str):
        """Tries to send a message to a websocket. if it fails, it removes the websocket from the list of active websockets"""
        try:
            await websocket.send(message)
        except:
            for socklist in cls.sockcon.values():
                if websocket in socklist:
                    socklist.remove(websocket)
                    print("removed websocket")
                    break

    @classmethod
    async def send_by_sockets(cls, websockets: list, message: str):
        """send message to all sockets in websockets"""
        await asyncio.gather(
            *[cls._try_send(websocket, message) for websocket in websockets]
        )

    @classmethod
    async def send_by_user(cls, user_id: int, message: str):
        """send message to all sockets in websockets"""
        await cls.send_by_sockets(cls.sockcon[user_id], message)

    @classmethod
    async def send_by_guild(cls, guild_id: int, message: str):
        """send message to all sockets subscribed to this guild"""
        await cls.send_by_sockets(cls.routing[guild_id], message)


class SlashCommands(SimpleNamespace):
    """This class does not need to be instantiated."""

    @staticmethod
    async def connect_badge(ctx, key: str):
        """Connect a badge to your user id"""

        user = ctx.author
        guild = ctx.guild

        key = key.upper()
        if not (
            ws := Conns.pending[key]
        ):  # If the key is invalid, do nothing and return
            await ctx.send("Invalid key")
            return

        if not (user_sockets := Conns.sockcon[user.id]):  # If the user has no badges
            Conns.sockcon[user.id] = [ws]
            print(f"new badge user: {user.name}")
        else:  # If the user already has a badge connected
            # use the key to connect the websocket to the badge user
            user_sockets.append(ws)
            print(f"new badge connected to user: {user.name}")

        # Add the user to the routing table
        if routes := Conns.routing[guild.id]:  # if the guild has a routing table
            routes.append(user_sockets)
        else:  # if the guild has no routing table
            Conns.routing[guild.id] = [user_sockets]

        # add the key to the keys table
        Conns.keyuser[key] = user_sockets

        # Acknoledge the connection
        msg = "connection accepted"
        await asyncio.gather(ws.send(msg), ctx.respond(msg))
        print(f"{user}'s Ipane is connected to {guild.name}")

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
        print(f"{ctx.author}'s Badges are enabled on {ctx.guild.name}")


class Notifiers(SimpleNamespace):
    @staticmethod
    def voice_change(msg, guild_id):
        """
        A user has changed voice channels.
        """

        if table := Conns.routing[guild_id]:
            pass
            # await asyncio.gather(*[bu.send_to_badges(message) for bu in badge_users])


from util import key_generator

# This is a callback function used by the websocket server
async def receive_new_websocket(websocket: websockets.WebSocketServerProtocol) -> None:
    """Receive a new websocket connection and add it to the pending connections table"""
    try:
        async for message in websocket:
            if message == "connect":
                key = key_generator(7)
                Conns.pending[key] = websocket
                print(f"key: {key} wants to connect")
                await websocket.send("connection waiting:" + key)

            elif message.startswith("reconnect"):
                await websocket.send("connection waiting")
                key = message.split(":")[1]
                # if the key is found
                if badge_user := Conns.keyuser[key]:
                    badge_user.websockets[key] = websocket
                    await websocket.send("connection accepted")
                    print(f"key: {key} reconnected")
                else:
                    await websocket.send("connection denied")
                    print(f"key: {key} wants to reconnect but key is not known")

    except:
        print("A connection has been interrupted")
