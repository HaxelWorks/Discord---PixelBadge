import string
import random


def key_generator(size, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))



def remove_unicode(string):
    return "".join(i for i in string if ord(i) < 128)
