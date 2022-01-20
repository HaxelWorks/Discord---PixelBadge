## Pretty clock
## just to annoy Tom because i can't be bothered to do a pull request
## added multiple colors. Up/Down control them
## Added timezone support
## Set up your timezone from the terminal by entering:
## machine.nvs_setstr('system', 'timezone', 'YOURTIMEZONE')
## Get your YOURTIMEZONE from 
## https://remotemonitoringsystems.ca/time-zone-abbreviations.php

import rgb, wifi, buttons, defines, system, machine, time
from default_icons import animation_connecting_wifi, icon_no_wifi

direction = 0
brightness = rgb.getbrightness()
rgb.clear()
rtc=machine.RTC()
timezone = machine.nvs_getstr('system', 'timezone')
if timezone is None:
  timezone = 'CET-1CEST-2,M3.5.0/02:00:00,M10.5.0/03:00:00'
machine.RTC().timezone(timezone)

# colors
colors = [
    # white, red, purple, blue, teal, green, yellow
    (255, 255, 255),
    (255,   0,   0),
    (255,   0, 255),  
    (  0,   0, 255),
    (  0, 255, 255),
    (  0, 255,   0),
    (255, 255,   0),  
]

color = 1

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
        print('No wifi')
        rgb.clear()
        rgb.framerate(20)
        data, frames = icon_no_wifi
        rgb.image(data, (12, 0), (8,8))
        time.sleep(3)
        rgb.clear()

if not wifi.status():
    print("Error connecting to wifi")
    system.reboot()

while rtc.now()[0]==1970:
    rtc.ntp_sync('pool.ntp.org')



UP, DOWN, LEFT, RIGHT = defines.BTN_UP, defines.BTN_DOWN, defines.BTN_LEFT, defines.BTN_RIGHT
A, B = defines.BTN_A, defines.BTN_B

def input_up(pressed):
    global direction
    direction = UP

def input_down(pressed):
    global direction
    direction = DOWN

def input_left(pressed):
    global direction
    direction = LEFT

def input_right(pressed):
    global direction
    direction = RIGHT

def input_B(pressed):
    global direction
    direction = B
	
def input_A(pressed):
    global direction
    direction = A

buttons.register(UP, input_up)
buttons.register(DOWN, input_down)
buttons.register(LEFT, input_left)
buttons.register(RIGHT, input_right)
buttons.register(B, input_B)
buttons.register(A, input_B)

tmold = 70
rgb.background((0,0,0))
rgb.clear()
rgb.framerate(1)

import util

# main loop
def run_clock():
    while direction != B:
        if direction == DOWN:
            color = (color - 1) % (len(colors))
            direction = 0
            print(color)
            tmold = 70
            time.sleep(0.5)
        if direction == UP:
            color = (color + 1) % (len(colors))
            direction = 0
            print(color)
            tmold = 70
            time.sleep(0.5)
        if direction == LEFT:
            if brightness > 3:
            brightness=brightness-1
            rgb.brightness(brightness)
            print(brightness)
            direction = 0
        if direction == RIGHT:
            if brightness < 32:
            brightness=brightness+1
            rgb.brightness(brightness)
            print(brightness)
            direction = 0
            
            
        th = rtc.now()[3]
        tm = rtc.now()[4]
        sth = '%02d' % th
        stm = '%02d' % tm
        if tm != tmold:
            rgb.clear()
            rgb.text(sth, colors[color], (3, 0))
            rgb.text(stm, colors[color], (18, 0))
            tmold = tm
        time.sleep(0.2)
        
