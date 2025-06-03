# Simple Metal Detector with Raspberry Pi

## Project Overview

This project is a simple metal detector based on the HMC5883L magnetic field sensor (on the GY-86 module) and a Raspberry Pi. The device detects the proximity of metallic objects and indicates this with LEDs: the closer the object, the more LEDs light up (up to 4).

## How It Works

1. **Power the device.**
2. **Press the START button** to begin detection.
3. Move a metallic object towards the sensor.
4. LEDs indicate proximity:
   - **1 LED**: object is far
   - **2-3 LEDs**: object is getting closer
   - **4 LEDs**: object is very close

## Measurement & Signal Processing

- The HMC5883L sensor measures magnetic field values on X, Y, and Z axes.
- The constant (DC) component for each axis is removed through calibration (moving the sensor in all directions).
- The **magnitude** of the magnetic field is calculated and used to control the LEDs.
- Thresholds for LED activation are determined experimentally.

## LED Indication Levels

- **No LEDs**: No metal detected nearby
- **1 LED**: Metal detected far from sensor
- **2 LEDs**: Metal is closer
- **3 LEDs**: Metal is significantly closer (two green, one red)
- **4 LEDs**: Metal is very close (two green, two red)

## User Instructions

1. Connect the device to power.
2. Press the START button to begin measurement.
3. Observe the LEDs as you move a metal object close to the sensor.
4. Disconnect power to stop the device.

## Demo

- [Demo Video]((https://youtu.be/aGgYZl3RPeY))

## Components

- Raspberry Pi (any model with GPIO)
- GY-86 module (with HMC5883L)
- 4 LEDs (2 green, 2 red)
- Button
- Resistors, wires, breadboard

## Example Code Snippet

```python
# See TECHNICAL_DOCUMENTATION.md for details and wiring diagram
import smbus
import RPi.GPIO as GPIO
import time

# ...setup and calibration code...

def read_magnetic_field():
    # Read and process sensor data
    pass

def display_leds(level):
    # Light up correct number of LEDs based on proximity
    pass

while True:
    if GPIO.input(BUTTON_PIN) == GPIO.HIGH:
        break

while True:
    field_strength = read_magnetic_field()
    level = calculate_level(field_strength)
    display_leds(level)
    time.sleep(0.1)
```

## Calibration

- Each axis (X, Y, Z) must be calibrated to remove DC offset.
- Magnitude thresholds for LEDs are set based on experimental measurements.

---

For more details, see [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md).
