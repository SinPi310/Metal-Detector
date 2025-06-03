import smbus
import time
import math

def read_byte(adr):
    return bus.read_byte_data(address, adr)
def read_word(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr+1)
    val = ((high << 8) | low)
    return val
def read_word_2c(adr):
    val = read_word(adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val
bus = smbus.SMBus(0)
address = 0x1e

for i in range(1, 1201):
    time.sleep(0.5)

    bus.write_byte_data(address, 0, 0x70)
    bus.write_byte_data(address, 0x01, 0xe0)
    bus.write_byte_data(address, 0x02, 0)

    bus.write_byte_data(address, 0x02, 0)
    mag_xout = read_word_2c(0x03)
    mag_yout = read_word_2c(0x05)
    mag_zout = read_word_2c(0x07)

    print("x:", mag_xout, "y:", mag_yout, "z:", mag_zout)