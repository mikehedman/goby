# from https://learn.adafruit.com/adafruit-lis3dh-triple-axis-accelerometer-breakout/python-circuitpython

# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import busio
import digitalio
import adafruit_lis3dh

int1 = digitalio.DigitalInOut(board.D22) # Set to correct pin for interrupt!

# Hardware I2C setup. Use the CircuitPlayground built-in accelerometer if available;
# otherwise check I2C pins.
if hasattr(board, "ACCELEROMETER_SCL"):
    i2c = busio.I2C(board.ACCELEROMETER_SCL, board.ACCELEROMETER_SDA)
    lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x19, int1=int1)
else:
    i2c = board.I2C()  # uses board.SCL and board.SDA
    # i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
    lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, int1=int1)

# Hardware SPI setup:
# spi = board.SPI()
# cs = digitalio.DigitalInOut(board.D5)  # Set to correct CS pin!
# lis3dh = adafruit_lis3dh.LIS3DH_SPI(spi, cs)

# PyGamer or MatrixPortal I2C Setup:
# i2c = board.I2C()  # uses board.SCL and board.SDA
# lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x19)


# Set range of accelerometer (can be RANGE_2_G, RANGE_4_G, RANGE_8_G or RANGE_16_G).
lis3dh.range = adafruit_lis3dh.RANGE_2_G

# listen for double tap
lis3dh.set_tap(2, 80)

# Loop forever printing accelerometer values
while True:
    # Read accelerometer values (in m / s ^ 2).  Returns a 3-tuple of x, y,
    # z axis values.  Divide them by 9.806 to convert to Gs.
    x, y, z = [
        value / adafruit_lis3dh.STANDARD_GRAVITY for value in lis3dh.acceleration
    ]
    print("x = %0.3f G, y = %0.3f G, z = %0.3f G" % (x, y, z))

    if lis3dh.tapped:
        print("Tapped!")
    if lis3dh.shake(shake_threshold=15):
        print("Shaken!")
    # Small delay to keep things responsive but give time for interrupt processing.
    time.sleep(0.1)
