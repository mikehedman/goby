import logging
import sys
import threading
import time
from enum import IntEnum
from os import mkdir
from os.path import join

import RPi.GPIO as GPIO
import adafruit_lis3dh
import board
import busio
import cv2
import digitalio
import numpy as np
import tflite_runtime.interpreter as tflite
from picamera2 import Picamera2

class Classification(IntEnum):
    BAD = 0
    GOOD = 1
    LEFT = 2
    RIGHT = 3
    WALL = 4

# Allow for a command line argument in seconds to allow for time to seal the bag and get in the pool
if len(sys.argv) > 1:
    time.sleep(int(sys.argv[1]))

ACCELEROMETER_X_THRESHOLD = .3 # swimmer facing down is 0, upright is -1
ACCELEROMETER_Y_THRESHOLD = .1 # swimmer rotating left to right, 0 is straight down

PREDICTION_THRESHOLD = .4 # 40% probability is the minimum to consider a prediction, otherwise skip it

IMAGE_INTERVAL = 1 #seconds
ACCELEROMETER_INTERVAL = .1 #seconds
RIGHT_GPIO = 17
LEFT_GPIO = 27
BUZZ_DURATION = 1

WIDTH = 640
HEIGHT = 480

# Load the TFLite model and allocate tensors.
MODEL_FILE= 'lane_classification_model.tflite'
IMAGES_DIR = '/home/mike/dev/goby/images'

session_time_string = str(time.time())
session_dir = join(IMAGES_DIR, session_time_string)
mkdir(session_dir)

logging.basicConfig(level=logging.INFO,
                    format='%(created)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler(join(session_dir, 'goby_logs.log')),
                              logging.StreamHandler()]
                    )
logging.info('Starting goby.py')

interpreter = tflite.Interpreter(
    model_path=MODEL_FILE,
    experimental_preserve_all_tensors=True
)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def setup_accelerometer():
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

    lis3dh.range = adafruit_lis3dh.RANGE_2_G
    return lis3dh

def setup_camera():
    picam = Picamera2()
    config = picam.create_preview_configuration()
    config['main']['size'] = (WIDTH, HEIGHT)
    config['main']['format'] = "RGB888"
    # config['main']['format'] = "YUV420"
    picam.align_configuration(config)
    picam.configure(config)
    picam.start()
    # allow the camera to warmup
    time.sleep(2)
    return picam

def buzz(pin, duration):
    GPIO.output(pin, True)
    logging.debug(str(pin) + " on")
    time.sleep(duration)
    GPIO.output(pin, False)
    logging.debug(str(pin) + " off")

def buzzWall():
    jumps = 3
    for i in range(jumps):
        GPIO.output(RIGHT_GPIO, True)
        time.sleep(BUZZ_DURATION / 2)
        GPIO.output(RIGHT_GPIO, False)
        GPIO.output(LEFT_GPIO, True)
        time.sleep(BUZZ_DURATION / 2)
        GPIO.output(LEFT_GPIO, False)

def buzzBad(duration):
    GPIO.output(RIGHT_GPIO, True)
    GPIO.output(LEFT_GPIO, True)
    time.sleep(duration)
    GPIO.output(RIGHT_GPIO, False)
    GPIO.output(LEFT_GPIO, False)

# from https://www.geeksforgeeks.org/how-to-implement-softmax-and-cross-entropy-in-python-and-pytorch/
def softmax(values):
  # Computing element wise exponential value
  exp_values = np.exp(values)
  exp_values_sum = np.sum(exp_values)
  return exp_values / exp_values_sum

def threaded_save_image(image, filename):
    cv2.imwrite(filename, image)

def save_image(image, classification_text, image_name):
    filename = join('/home/mike/dev/goby/images', session_time_string, classification_text, image_name)
    threading.Thread(target=threaded_save_image, args=(image, filename)).start()

def make_dir(dir):
  try:
    mkdir(dir)
  except FileExistsError:
    pass

def setup_dirs():
  make_dir(join(session_dir, "bad"))
  make_dir(join(session_dir, "good"))
  make_dir(join(session_dir, "left"))
  make_dir(join(session_dir, "right"))
  make_dir(join(session_dir, "wall"))
  make_dir(join(session_dir, "unclassified"))

def evaluate_image(image):

    img_array = np.expand_dims(image, axis=0)
    img_array = np.float32(img_array) / 255.0
    #flip the order of the image data, since the image files are in BGR rather than RGB
    img_array = img_array[...,::-1]
    interpreter.set_tensor(input_details[0]['index'], img_array)

    interpreter.invoke()

    output_data = interpreter.get_tensor(output_details[0]['index'])
    results = np.squeeze(output_data)
    score = softmax(results)
    probability = 100 * np.max(score)

    image_name = f'{time.time()}.png'

    if probability > PREDICTION_THRESHOLD:
        classification = np.argmax(score)
        logging.info(f'before classification with {image_name} ')
        match classification:
            case Classification.BAD:
                classification_text = "bad"
                save_image(image, "bad", image_name)
                buzzBad(BUZZ_DURATION * 1.5)
                logging.info(f'{image_name} - Bad image, probability: {probability}')
            case Classification.GOOD:
                classification_text = "good"
                save_image(image, "good", image_name)
                logging.info(f'{image_name} - Good image, probability: {probability}')
            case Classification.LEFT:
                classification_text = "left"
                save_image(image, "left", image_name)
                buzz(LEFT_GPIO, BUZZ_DURATION)
                logging.info(f'{image_name} - Left image, probability: {probability}')
            case Classification.RIGHT:
                classification_text = "right"
                save_image(image, "right", image_name)
                buzz(RIGHT_GPIO, BUZZ_DURATION)
                logging.info(f'{image_name} - Right image, probability: {probability}')
            case Classification.WALL:
                classification_text = "wall"
                save_image(image, "wall", image_name)
                buzzWall()
                logging.info(f'{image_name} - Wall image, probability: {probability}')
    else:
        classification_text = "unclassified"
        logging.info(f'{image_name} - Skipping image, probability too low: {probability}')
    save_image(image, classification_text, image_name)


def main():
    setup_dirs()

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(RIGHT_GPIO, GPIO.OUT)
    GPIO.setup(LEFT_GPIO, GPIO.OUT)

    # initialize the camera and grab a reference to the raw camera capture
    camera = setup_camera()
    logging.info('Camera setup complete')
    lis3dh = setup_accelerometer()
    logging.info('Accelerometer setup complete')

    # send startup buzz
    buzz(RIGHT_GPIO, .5)
    buzz(LEFT_GPIO, .5)
    logging.info('Startup buzz complete')
    while True:
        try:
            # should we take a picture?
            x, y, z = [
                value / adafruit_lis3dh.STANDARD_GRAVITY for value in lis3dh.acceleration
            ]
            # print("x = %0.3f G, y = %0.3f G, z = %0.3f G" % (x, y, z))
            if abs(x) < ACCELEROMETER_X_THRESHOLD and abs(y) < ACCELEROMETER_Y_THRESHOLD:
                try:
                    image = camera.capture_array()
                    cameraImage = image[:HEIGHT, :WIDTH]
                    rotatedImage = cv2.rotate(cameraImage, cv2.ROTATE_90_CLOCKWISE)
                    evaluate_image(rotatedImage)
                finally:
                    time.sleep(IMAGE_INTERVAL)
            else:
                time.sleep(ACCELEROMETER_INTERVAL)
        except Exception as e:
            logging.exception("An error occurred: {}".format(e))

main()
GPIO.cleanup()

