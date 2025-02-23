# goby
A system to give feedback to visually impaired swimmers when they are not in the center of the lane, or approaching a wall.

> [!NOTE]
> This project is a work in progress. Real world testing is currently showing 87% accuracy of the classifications.
> [@Animar123](https://github.com/Animar123) is working on a GAN utility to increase the number of training images, which should help resolve the model's overfitting.

## Background
This project is based on the ideas explored in the University of Colorado research project titled "Goby". The lead researcher has graciously agreed to allow us to take up the name, and has provided helpful insights and guidance on our implementation. [Original writup](https://www.annika.co/files/Wearable-Swimming-Aid-Muehlbradt.pdf), [alternative link]( https://dl.acm.org/doi/pdf/10.1145/3132525.3134822).

## System components
Raspberry Pi 5, vibration motors, battery, camera, waterproof bag, accelerometer 

## Software description
There are two main components to the software:
1. The main app `goby.py`, which runs on the Raspberry Pi, and collects images from the camera, and sends them to the model for classification.
2. The model builder `classification.py`, which is a TensorFlow model, and is trained to classify images as "good", "left", "right", or "wall".
There are also some utilities, like the `prepare_model_inputs.py` scritpt, which is used to prepare the model inputs.

Included is the original Canny Edge Detection code, which is used to detect the edges of the lane lines. This code is not used in the final implementation, but is included for reference. Shout out to [@Animar123](https://github.com/Animar123) for starting up this effort!

### Developer setup
Running the `classification.py` script in a venv with tensorflow-metal made building the model run much faster!

TODO:  Add instructions for setting up the venv

### Installation on Raspberry Pi
TODO:  Add instructions for installing the software libraries on the Raspberry Pi

The program runs at bootup via systemctl.  The service file is located at /lib/systemd/system/goby.service:
```
[Unit]
Description=Image Collector Service

[Service]
ExecStart=/home/mike/dev/goby/.venv/bin/python3 /home/mike/dev/goby/goby.py

[Install]
WantedBy=multi-user.target
```
Note: you would want to change the paths to match your setup.

### How to run

## Model curation
When in use, the main goby.py app collects images, and stores them in a set of directories based on their predicted classification.  These images need to be checked, and moved to the proper directory. The sorted folders are then moved to the /ai/images/originals folder.
Prior to (re)training the model, run /ai/utilities/prepare_model_inputs.py  This script cycles through all the image sets in the "originals" folder, and: 
1. Copies the images to the training_set directory
2. Breaks out a set of the images for a prediction (validation) set
2. Uses data augmentation to create additional images:
   3. creates "left" and "right" images by flipping the original image horizontally
   4. creates a "good" image by flipping wall images vertically, and conversely flips "flippable" good images vertically to create a "wall" image. (Flippable images have a cross, but were collected when the swimmer was pushing away from the wall)
   5. creates new "good" images by flipping the original image vertically, and then also horizontally
6. 
    

## Credits
Pool water images from Freepik https://www.freepik.com/
<a href="https://www.freepik.com/free-photo/pool-water-background_3963032.htm#from_view=detail_alsolike">Image by lifeforstock on Freepik</a>
<a href="https://www.freepik.com/free-photo/beautiful-shot-rippling-crystal-blue-water-background_7747850.htm#fromView=search&page=1&position=4&uuid=4cd217db-ce4e-4bc5-b7c7-18e5b17dc077">Image by wirestock on Freepik</a>
