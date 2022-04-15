from collections import defaultdict
import yaml
from os import path
import atexit
preferences = dict()
scoretable = defaultdict(lambda: defaultdict(float))

def register(user_id, guild_id, side):
    scoretable[guild_id][user_id] = 0
    preferences[guild_id][user_id] = websocket

def joined(user_id, guild_id):
    scoretable[guild_id][user_id] += 1


def rooting():
    """we normalize the scores by replacing all of them by their square roots
    This keeps the system dynamic, but also keeps the scores from being too big
    """
    for guild_id in scoretable:
        for user_id in scoretable[guild_id]:
            scoretable[guild_id][user_id] **= 0.5


def muted(user_id, guild_id, state: bool):
    return False


def save():
    with open(path.join(path.dirname(__file__), "conns.yml"), "w") as f:
        yaml.dump(dict(scoretable), f)
atexit.register(save)

# load , we dont need a function for this
