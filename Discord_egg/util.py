import rgb, wifi, system, time
from default_icons import animation_connecting_wifi, icon_no_wifi
from math import pi, sin

FRAMERATE = 30


# color definitions
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
BLUE = (0, 0, 255)


def hex_to_rgb(hex_color):
    # convert hex color to rgb tuple
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

def countdown(seconds):
    for i in range(seconds):
        rgb.clear()
        rgb.text(str(seconds-i))
        time.sleep(1)



def blip(color):
    rgb.pixel(color, (0, 0))
    time.sleep(0.3)
    rgb.pixel(BLACK, (0, 0))
    
def connect_wifi():
    # connect WIFI
    if not wifi.status():
        data, size, frames = animation_connecting_wifi
        rgb.clear()
        rgb.framerate(3)
        rgb.gif(data, (12, 0), size, frames)
        wifi.connect()
        if wifi.wait():
            rgb.clear()
            rgb.framerate(20)
        else:
            print("No wifi")
            rgb.clear()
            rgb.framerate(20)
            data, frames = icon_no_wifi
            rgb.image(data, (12, 0), (8, 8))
            time.sleep(3)
            rgb.clear()
    if not wifi.status():
        print("Error connecting to wifi")
        system.reboot()


# Function that removes unicode characters from a string
def remove_unicode(string):
    return "".join(i for i in string if ord(i) < 128)


def notify(who, what, guild, channel):
    # Select the right color
    if what == "joined":
        color = GREEN
    elif what == "left":
        color = RED
    elif what == "moved to":
        color = ORANGE
    else:
        color = WHITE

    text = remove_unicode(who + " " + what + " " + guild + " " + channel)
    scroll_time = 6 * len(text) / FRAMERATE
    rgb.clear()
    rgb.framerate(FRAMERATE)
    rgb.brightness(32)

    # Flash the display n times
    for _ in range(3):
        rgb.background(color)
        time.sleep(0.15)
        rgb.background(BLACK)
        time.sleep(0.2)

    rgb.brightness(0)

    rgb.scrolltext(text, color)
    time.sleep(scroll_time)
    rgb.clear()


# Function that removes unicode characters from a string
def remove_unicode(string):
    return "".join(i for i in string if ord(i) < 128)
