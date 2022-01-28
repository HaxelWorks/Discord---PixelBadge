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


class ConnStore:
    """
    Contains all the connections.
    This class does not need to be instantiated.
    """

    pending = defaultdict(lambda: None)  # key: key, value: websocket
    routing = defaultdict(lambda: None)  # guild_id -> [BadgeUser]
    users = defaultdict(lambda: None)  # key: UserId, value: BadgeUser
    known_keys = defaultdict(lambda: None)  # key: key, value: BadgeUser
    
    # @classmethod
    # def save_store():
    #     pass
        


# def save_store():
#     """save the routing,users and known_keys to a dictionary which will then be pickled"""
#     with open("data.pkl", "wb") as f:
#         pickle.dump(
#             {
#                 "routing": ConnStore.routing,
#                 "users": ConnStore.users,
#                 "known_keys": ConnStore.known_keys,
#             },
#             f,
#         )


# atexit.register(save_store)


# def load():
#     """load the routing,users and known_keys from a dictionary which was pickled"""
#     # if the file does not exist, return
#     if not path.exists("data.pkl"):
#         return
#     with open("data.pkl", "rb") as f:
#         for key, value in pickle.load(f):
#             setattr(ConnStore, key, value)


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
            print(f"{self.user}'s connection {key} is has been lost")
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
            ws := ConnStore.pending[key]
        ):  # If the key is invalid, do nothing and return
            await ctx.send("Invalid key")
            return

        if not (badge_user := ConnStore.users[user.id]):  # If the user has no badges
            badge_user = ConnStore.users[user.id] = BadgeUser(
                ws, key, user, guild
            )  # create a new badge user
            print(f"new badge user: {user.name}")
        else:  # If the user already has a badge connected
            badge_user.websockets[
                key
            ] = ws  # use the key to connect the websocket to the badge user
            print(f"new badge connected to user: {user.name}")

        # Add the user to the routing table
        if routes := ConnStore.routing[guild.id]:  # if the guild has a routing table
            routes.append(badge_user)
        else:  # if the guild has no routing table
            ConnStore.routing[guild.id] = [badge_user]

        # add the key to the keys table
        ConnStore.known_keys[key] = badge_user

        # Acknoledge the connection
        msg = "connection accepted"
        await asyncio.gather(ws.send(msg), ctx.respond(msg))
        print(f"{user}'s Ipane is connected to {guild.name}")

        # Clean up the pending connections
        ConnStore.pending.pop(key)

    @staticmethod
    async def enable_notifications(ctx):
        """Enable notifications for this server"""

        if not (
            badge_user := ConnStore.users[ctx.author.id]
        ):  # If the user has no badges
            await ctx.respond("You have no badge connected")
            return

        if table := ConnStore.routing[ctx.guild.id]:  # if the guild has a routing table
            table.append(badge_user)
        else:  # if the guild has no routing table
            ConnStore.routing[ctx.guild.id] = [badge_user]
        await ctx.respond("Enabled")
        print(f"{ctx.author}'s Badges are enabled on {ctx.guild.name}")


# We load after the class definitions
# load()


from util import key_generator

# This is a callback function used by the websocket server
async def receive_new_websocket(websocket: websockets.WebSocketServerProtocol) -> None:
    """Receive a new websocket connection and add it to the pending connections table"""
    try:
        async for message in websocket:
            if message == "connect":
                key = key_generator(7)
                ConnStore.pending[key] = websocket
                print(f"key: {key} wants to connect")
                await websocket.send("connection waiting:" + key)

            elif message.startswith("reconnect"):
                await websocket.send("connection waiting")
                key = message.split(":")[1]
                # if the key is found
                if badge_user := ConnStore.known_keys[key]:
                    badge_user.websockets[key] = websocket
                    await websocket.send("connection accepted")
                    print(f"key: {key} reconnected")
                else:
                    await websocket.send("connection denied")
                    print(f"key: {key} wants to reconnect but key is not known")

    except:
        print("A connection has been interrupted")
