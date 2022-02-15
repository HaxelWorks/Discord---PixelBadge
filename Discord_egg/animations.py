from math import sin, pi,sqrt
def center_wave(scale, fps, frames=30, origin=(16.5, 4.5)):
    """Displays a ripple on the 32x8 matrix using sine waves"""
    rgb.disablecomp()  # disable compositor
    for frame in range(frames):
        # the generated frame needs to be in a list with the format 0x00rrggbb.
        for x in range(32):
            for y in range(8):
                d = (x - origin[0])**2 + (y - origin[1])**2
                d = sqrt(d)
                brightness = int(sin(d * scale * pi) * 127 + 128)