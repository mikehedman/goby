import RPi.GPIO as GPIO
import time

RIGHT = 17
LEFT = 27
GPIO.setmode(GPIO.BCM)

def buzz(pin, duration):
    GPIO.output(pin, True)
    print(str(pin) + " on")
    time.sleep(duration)
    GPIO.output(pin, False)
    print(str(pin) + " off")

def buzzBoth(duration):
    GPIO.output(RIGHT, True)
    GPIO.output(LEFT, True)
    print("both on")
    time.sleep(duration)
    GPIO.output(RIGHT, False)
    GPIO.output(LEFT, False)
    print("both off")

GPIO.setwarnings(False)
GPIO.setup(RIGHT,GPIO.OUT)
GPIO.setup(LEFT,GPIO.OUT)

# while True:
buzz(RIGHT, 1)
time.sleep(1)
buzz(LEFT, 1)
time.sleep(1)

# both
buzzBoth(1)

GPIO.cleanup()