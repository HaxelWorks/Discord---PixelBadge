import rgb
import time
from math import pi, sin
FRAMERATE = 30


# color definitions
white = (255, 255, 255)
black = (0,0,0)
green = (0,255,0)
red = (255,0,0)
orange = (255,165,0)



def notify(who,what,guild,channel):
    # Select the right color
    if what == "joined":
        color = green
    elif what == "left":
        color = red
    elif what == "moved to":
        color = orange
    else:
        color = white
    
    text = who + " " + what + " " + guild + " " + channel
    scroll_time = 7*len(text)/FRAMERATE
    rgb.clear()
    rgb.framerate(FRAMERATE)
    rgb.brightness(16)
    
    # Flash the display n times
    for _ in range(3):
        rgb.background(color)
        time.sleep(0.15)
        rgb.background(black)
        time.sleep(0.2)
        
    rgb.brightness(0)
    rgb.scrolltext(text, color)
    time.sleep(scroll_time)
    rgb.clear()
  
    
