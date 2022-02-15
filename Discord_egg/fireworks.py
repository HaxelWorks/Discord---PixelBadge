import rgb, virtualtimers
from random import randint, random, choice

steps = [([0xFFFFFFFF], 1, 1),
         ([0, 0xFFFFFFFF, 0, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0, 0xFFFFFFFF, 0], 3, 3),
         ([0xFFFFFFFF, 0, 0xFFFFFFFF, 0, 0xFFFFFFFF, 0, 0xFFFFFFFF, 0, 0xFFFFFFFF], 3, 3),
         ([0xFFFFFFFF, 0, 0, 0, 0xFFFFFFFF,
           0, 0xFFFFFFFF, 0, 0xFFFFFFFF, 0,
           0, 0, 0xFFFFFFFF, 0, 0,
           0, 0xFFFFFFFF, 0, 0xFFFFFFFF, 0,
           0xFFFFFFFF, 0, 0, 0, 0xFFFFFFFF, ], 5, 5)]

n_steps = len(steps)

RED = 0xFF0000FF
GREEN = 0x00FF00FF
BLUE = 0x0000FFFF
YELLOW = 0xFFFF00FF
ORANGE = 0xFF6F00FF
PURPLE = 0xFF00FFFF

COLOURS = [RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE]

class Firework:
    x = None
    y = None
    target = None
    step = None
    speed = None
    colour = None
    max_size = None

    def __init__(self, x, y, target, step, speed, colour, max_size):
        self.x = x
        self.y = y
        self.target = target
        self.step = step
        self.speed = speed
        self.colour = colour
        self.max_size = max_size

def make_firework():
    x = randint(0, 31)
    y = randint(8, 16)
    target = randint(0, 6)
    step = 0
    speed = 0.2 + (random() * 1.8)
    colour = choice(COLOURS)
    max_size = randint(2, n_steps)
    return Firework(x, y, target, step, speed, colour, max_size)

def replace_colour(data, colour):
    return [colour if val else 0 for val in data]

n_fireworks = 5
fireworks = [make_firework() for _ in range(n_fireworks)]

def draw_firework(firework):
    if firework.y > firework.target:
        color=((firework.colour & 0xFF000000) >> 24,
               (firework.colour & 0x00FF0000) >> 16,
               (firework.colour & 0x0000FF00) >> 8)
        rgb.pixel(color=(255,255,255),
                  pos=(firework.x, round(firework.y)))
    elif firework.step < n_steps:
        data, width, height = steps[firework.step]
        rgb.image(replace_colour(data, firework.colour),
                  pos=(round(firework.x - (width-1)/2), round(firework.y - (height-1)/2)), size=(width, height))


def update():
    rgb.disablecomp()
    rgb.clear()
    for index, firework in enumerate(fireworks):
        if firework is None:
            firework = make_firework()
            fireworks[index] = firework
        draw_firework(firework)
        if firework.y > firework.target:
            firework.y -= firework.speed
        elif firework.step < firework.max_size:
            firework.step += 1
        else:
            fireworks[index] = make_firework()
    rgb.enablecomp()
    return 50


virtualtimers.begin(50)
virtualtimers.new(0, update)