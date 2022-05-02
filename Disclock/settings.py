import valuestore

clock_red = 255
clock_green = 0
clock_blue = 0
clock_brightness = 6

animation_brightness = 32

#Try to load previous settings     
try:
    clock_color = valuestore.load('Discord', 'clock_color')
    
    for k, v in clock_color.items():
        globals()[k] = v
except:
    print("No settings found")
    
