import string
import random


def key_generator(size, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


def remove_unicode(string):
    return "".join(i for i in string if ord(i) < 128)


def rgb_to_hex(rgb):
    """turn an rgb tuple into a hex string"""
    return "#%02x%02x%02x" % rgb


class Colors:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    ORANGE = (255, 165, 0)
    BLUE = (0, 0, 255)


if __name__ == "__main__":
    colors = [
        Colors.WHITE,
        Colors.BLACK,
        Colors.GREEN,
        Colors.RED,
        Colors.ORANGE,
        Colors.BLUE,
    ]
    for col in colors:
        print(rgb_to_hex(col))
