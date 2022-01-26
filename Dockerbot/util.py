import string
import random

def key_generator(size, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))

# Function that removes unicode characters from a string
def remove_unicode(string):
    return "".join(i for i in string if ord(i) < 128)



import logging
LOG_PATH = "Dockerbot/logs"

logFormatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
LOGGER = logging.getLogger()

fileHandler = logging.FileHandler("{0}/{1}.log".format(LOG_PATH, "log1"))
fileHandler.setFormatter(logFormatter)
LOGGER.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
LOGGER.addHandler(consoleHandler)
LOGGER.setLevel(logging.INFO)