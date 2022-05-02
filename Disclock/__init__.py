"""
Discord Notifications and Clock for Ipane and PixelBadge
by Axel Roijers

"""


APP_NAME="disclock"
import sys
# We would like to import modules that are added to his folder.

sys.path.append("/apps/" + APP_NAME)

import usocket as socket
import ubinascii as binascii
import ussl
import util
import valuestore
from util import notify, connect_wifi
from util import RED, GREEN, BLUE
from protocol import Websocket, urlparse
import rgb, system, machine, time
import urandom as random
from simple_clock import update_clock
import settings
import json

rgb.framerate(30)
interrupt = False


class WebsocketClient(Websocket):
    is_client = True


def connect_websocket(uri):
    # WARNING: i have no idea how this works but it works
    """
    Connect a websocket.
    """

    uri = urlparse(uri)
    assert uri

    # if __debug__: LOGGER.debug("open connection %s:%s",
    #                             uri.hostname, uri.port)

    sock = socket.socket()
    addr = socket.getaddrinfo(uri.hostname, uri.port)
    sock.connect(addr[0][4])
    if uri.protocol == "wss":
        sock = ussl.wrap_socket(sock)

    def send_header(header, *args):
        # if __debug__: LOGGER.debug(str(header), *args)
        sock.write(header % args + "\r\n")

    # Sec-WebSocket-Key is 16 bytes of random base64 encoded
    key = binascii.b2a_base64(bytes(random.getrandbits(8) for _ in range(16)))[:-1]

    send_header(b"GET %s HTTP/1.1", uri.path or "/")
    send_header(b"Host: %s:%s", uri.hostname, uri.port)
    send_header(b"Connection: Upgrade")
    send_header(b"Upgrade: websocket")
    send_header(b"Sec-WebSocket-Key: %s", key)
    send_header(b"Sec-WebSocket-Version: 13")
    send_header(
        b"Origin: http://{hostname}:{port}".format(hostname=uri.hostname, port=uri.port)
    )
    send_header(b"")

    header = sock.readline()[:-2]
    assert header.startswith(b"HTTP/1.1 101 "), header

    # We don't (currently) need these headers
    # FIXME: should we check the return key?
    while header:
        # if __debug__: LOGGER.debug(str(header))
        header = sock.readline()[:-2]

    return WebsocketClient(sock)


def connect_badgeserver(websocket):

    websocket.send("connect")
    rec = websocket.recv()
    if rec.startswith("connection waiting"):
        key = rec.split(":")[1]  # key is the second part of the message
        rgb.clear()
        rgb.text(key)
        print(key)
    if websocket.recv() == "connection accepted":
        # save the key to nvs
        machine.nvs_setstr("Discord", "key", key)
        rgb.clear()
        rgb.scrolltext("Connected", GREEN)
        print("Connected")
    else:
        print("Connection failed")
        rgb.scrolltext("Failed", RED)
        time.sleep(6)


def reconnect_badgeserver(websocket, key):

    websocket.send("reconnect:" + key)
    rec = websocket.recv()
    if rec.startswith("connection waiting"):
        rgb.scrolltext("Reconnecting", BLUE)
        print("Reconnecting")
    if websocket.recv() == "connection accepted":
        rgb.clear()
        rgb.scrolltext("Waiting for next ping", GREEN)
        print("Connected")
    else:
        print("Connection failed")
        rgb.clear()
        rgb.scrolltext("Connection failed", RED)
        # throw an exception
        raise Exception("Connection failed")


def main(): 
    global interrupt
    connect_wifi()
    
    # connect websocket
    rgb.clear()
    rgb.scrolltext("Finding Hot servers in your area", BLUE)
    websocket = connect_websocket("ws://pixelbox.ddns.net:8765")
    print("Connected to server")
    websocket.settimeout(3600)
    rgb.clear()

    try:
        key = machine.nvs_getstr("Discord", "key")
        reconnect_badgeserver(websocket, key)
        print("Reconnected")
    except:
        connect_badgeserver(websocket)
        print("New connection")


    websocket.settimeout(120)
    while not interrupt: # Main loop
        rec = websocket.recv()
        if rec == "ping":
            print("pong")
            update_clock()
            
        # if json    
        elif rec[0] == "{" and rec[-1] == "}":
            json_data = json.loads(rec)
            valuestore.save("Discord", "clock_color", json_data)
            for k, v in json_data.items():
                setattr(settings, k, v)

            update_clock(force_draw=True)

        else:
            print(rec)
            msg,color = rec.split("#")
            notify(msg,color)
            update_clock(force_draw=True)
            

while not interrupt:
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting")
        interrupt = True
        break

print("rebooting")
system.reboot()
