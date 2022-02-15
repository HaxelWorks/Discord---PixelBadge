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
from itertools import chain


class Conns(SimpleNamespace):

    """
    Contains all the connections to badges
    This class does not need to be instantiated.
    """

    pending = dict()  #   key: key, value: websocket
    keystor = dict()  #   key: key, value: user_id
    subusrs = dict()  #   key: guild_id, value: [user_id] Subscribed users
    usrsock = dict()  #   key: user_id, value: [websocket]


    # Saving / Restoring connections
    @classmethod
    def save(cls):
        data = {
            "keystor": cls.keystor,
            "subusrs": cls.subusrs,
        }
        with open(path.join(path.dirname(__file__), "conns.yml"), "w") as f:
            yaml.dump(data, f)

    @classmethod
    def load(cls):
        # if the file does not exist, return
        if not path.exists(path.join(path.dirname(__file__), "conns.yml")):
            print("conns.yml does not exist")
            return

        with open(path.join(path.dirname(__file__), "conns.yml"), "r") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            cls.keystor = data["keystor"]
            cls.subusrs = data["subusrs"]

    # Sending methods
    @classmethod
    async def _try_send(cls, websocket, message: str):
        """Tries to send a message to a websocket. if it fails, it removes the websocket from the list of active websockets"""
        try:
            await websocket.send(message)
        except:
            for socklist in cls.usrsock.values():
                if websocket in socklist:
                    socklist.remove(websocket)
                    print("removed websocket")
                    break

    @classmethod
    async def send_broadcast(cls, msg: str):
        """Send a message to all active websockets in parallel"""
        # first we collect all the websockets
        all_socks = chain.from_iterable(cls.usrsock.values())
        tasks = [cls._try_send(ws, msg) for ws in all_socks]
        await asyncio.gather(*tasks)

    @classmethod
    async def send_by_sockets(cls, websockets: list, message: str):
        """send message to all sockets in websockets"""
        if not websockets or not message: # guard against empty lists
            return
        await asyncio.gather(
            *[cls._try_send(websocket, message) for websocket in websockets]
        )

    @classmethod
    async def send_by_user(cls, user_id: int, message: str):
        """send message to all sockets connected to user_id"""
        await cls.send_by_sockets(cls.usrsock.get(user_id), message)

    @classmethod
    async def send_by_guild(cls, guild_id: int, message: str):
        """send message to all sockets subscribed to this guild"""

        # collect all the relevant websockets
        if not (uids := cls.subusrs.get(guild_id)):  # guard against empty lists
            return
        sockets = [] # collects all the websockets
        for uid in uids:
            sockets.extend(cls.usrsock.get(uid, []))
        await cls.send_by_sockets(sockets, message)

# load the previous connections
Conns.load()
# register the save function to be called when the program exits
atexit.register(Conns.save)


class SlashCommands(SimpleNamespace):
    """This class does not need to be instantiated."""

    @staticmethod
    async def connect_badge(ctx, key: str):
        """Connect a badge to your user id"""

        user = ctx.author
        guild = ctx.guild

        key = key.upper()
        if not (
            ws := Conns.pending.get(key)
        ):  # If the key is invalid, do nothing and return
            await ctx.send("Invalid key")
            return

        if not (user_sockets := Conns.usrsock.get(user.id)):  # If the user has no badges
            Conns.usrsock[user.id] = [ws]
            print(f"new badge user: {user.name}")
        else:  # If the user already has a badge connected
            # use the key to connect the websocket to the badge user
            user_sockets.append(ws)
            print(f"new badge connected to user: {user.name}")

        # Add the user to the routing table
        if routes := Conns.subusrs.get(guild.id):  # if the guild has a routing table
            routes.append(user_sockets)
        else:  # if the guild has no routing table
            Conns.subusrs[guild.id] = [user.id] # create a new routing table

        # connect the user to the key
        Conns.keystor[key] = user.id

        # Acknoledge the connection
        msg = "connection accepted"
        await asyncio.gather(ws.send(msg), ctx.respond(msg))
        print(f"{user}'s Ipane is connected to {guild.name}")

        # Clean up the pending connection
        Conns.pending.pop(key)

    @staticmethod
    async def enable_notifications(ctx):
        """Enable notifications for this server"""

        if not (badge_user := Conns.users[ctx.author.id]):  # If the user has no badges
            await ctx.respond("You have no badge connected")
            return

        if table := Conns.subusrs[ctx.guild.id]:  # if the guild has a routing table
            table.append(badge_user)
        else:  # if the guild has no routing table
            Conns.subusrs[ctx.guild.id] = [badge_user]
        await ctx.respond("Enabled")
        print(f"{ctx.author}'s Badges are enabled on {ctx.guild.name}")


from util import key_generator

# This is a callback function used by the websocket server
async def receive_new_websocket(ws: websockets.WebSocketServerProtocol) -> None:
    """Receive a new websocket connection and add it to the pending connections table"""
    try:
        async for message in ws:
            if message.startswith("connect"):
                key = key_generator(size=5)
                Conns.pending[key] = ws
                print(f"key: {key} wants to connect")
                await ws.send("connection waiting:" + key)

            elif message.startswith("reconnect"):
                await ws.send("connection waiting")
                key = message.split(":")[1]
                # if the key is found
                if badge_user := Conns.keystor.get(key):
                    # add the websocket to the badge users websocket list
                    badge_user.websockets[key] = ws  
                    await ws.send("connection accepted")
                    print(f"key: {key} reconnected")
                else:  # if the key is not found
                    await ws.send("connection denied")
                    print(f"key: {key} wants to reconnect but key is not known")

    except:
        print("A connection has been interrupted")
