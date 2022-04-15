from enum import Enum
class Colors(): # ? for some reason enum fucks this up
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    ORANGE = (255, 145, 0)
    BLUE = (0, 0, 255)

def remove_unicode(string):
    return "".join(i for i in string if ord(i) < 128)


def rgb_to_hex(rgb: tuple):
    """turn an rgb tuple into a hex string"""
    return "#%02x%02x%02x" % rgb


if __name__ == "__main__":

    for col in Colors:
        print(rgb_to_hex(col))
