import Adafruit_SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from gpiozero import LED
import math

led1 = LED(17)
led2 = LED(27)
led3 = LED(22)
led4 = LED(23)

from gpiozero import Button

import json
import socket
import select

from sensors import *

# udp client (sender) configuration
# set destination IP and port -> your PC
UDP_IP = "192.168.99.2"
UDP_PORT = 5005
# udp clinet (listener) configuration
# set own IP to bind -> Raspberry Pi
UDP_IP_SELF = "192.168.99.1"
UDP_PORT_SELF = 5006

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

sock_in = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

sock_in.bind((UDP_IP_SELF, UDP_PORT_SELF))

# preapre buttons
button = []
button.append(Button(6))
button.append(Button(13))
button.append(Button(19))
button.append(Button(26))

# display initialization
disp = Adafruit_SSD1306.SSD1306_128_32(rst=None)
disp.begin()
disp.clear()
disp.display()
width = disp.width
height = disp.height
image = Image.new('1', (width, height))
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()

# clear working buffer of the display
draw.rectangle((0,0,width,height), outline=0, fill=0)

# print some text to working buffer
x = 0
top = -2
draw.text((x, top), "   Metal detector", font=font, fill=255)
draw.text((x, top + 8), "by Wojciech Hajduk", font=font, fill=255)
draw.text((x, top + 25), "START", font=font, fill=255)

# update the display
disp.image(image)
disp.display()


sensor = sensors()

while True:
    if button[0].is_pressed:
        while True:
            value = sensor.read_mag()
            x = value['x']
            y = value['y']
            z = value['z']

            if x >= -0.15 and x <= 0.2:
                x1 = False
            else:
                x1 = True

            if y >= -0.22 and y <= 0.01:
                y1 = False
            else:
                y1 = True

            if z >= -0.75 and z <= -0.4:
                z1 = False
            else:
                z1 = True

            if x1 == True or z1 == True or y1 == True:
                sume = (((x ** 2) + (y ** 2) + (z ** 2)) / 3) ** (1 / 2)
                print(sume)

                if sume > 0.35:
                    led4.on()
                else:
                    led4.off()

                if sume > 1:
                    led3.on()
                else:
                    led3.off()

                if sume > 2:
                    led2.on()
                else:
                    led2.off()

                if sume > 3.7:
                    led1.on()
                else:
                    led1.off()

            else:
                led1.off()
                led2.off()
                led3.off()
                led4.off()

    # terminate if button 0 pressed
    if button[0].is_pressed:
        break
    # when recieve any packet - measure and send data to PC
    ready = select.select([sock_in], [], [], 0.1)
    if ready[0]:
        message, address = sock_in.recvfrom(1024)
        mag = sensor.read_mag_raw()
        data = json.dumps(mag)
        sock.sendto(bytes(data, "utf-8"), (UDP_IP, UDP_PORT))
        time.sleep(0.1)

# display termination info
draw.rectangle((0,0,width,height), outline=0, fill=0)
draw.text((x, top), "   Metal detector", font=font, fill=255)
draw.text((x, top + 8), "by Wojciech Hajduk", font=font, fill=255)
draw.text((x, top + 16), "Terminated...", font=font, fill=255)
draw.text((x, top + 25), "START", font=font, fill=255)
disp.image(image)
disp.display()