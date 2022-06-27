import cv2
import numpy as np
import matplotlib.pyplot as plt
import math

def imageText(image, words):
    font = cv2.FONT_HERSHEY_SIMPLEX
    # org
    org = (50, 50)
    # fontScale
    fontScale = 1
    # Blue color in BGR
    color = (255, 0, 0)
    # Line thickness of 2 px
    thickness = 2
    # Using cv2.putText() method
    TI = cv2.putText(image, words, org, font, fontScale, color, thickness, cv2.LINE_AA)
    return TI

def canny(image):
    # GreyScale conversion
    grayImage = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # blur conversion
    # blur smooths the image by averaging around the pixels with the pixels around it
    # in my opinion not nescacry for what our image recognition is trying to do but may need it later (with shadow and other imperfections in the image)
    blurImage = cv2.GaussianBlur(grayImage, (5,5), 0)

    # canny conversion - allows you to find the change in color in an image by taking the derivative of pixels in the 2d array
    cannyImage = cv2.Canny(blurImage, 50, 150)

    return cannyImage
# use algorythm to find region of intrest

def getPointsOfChangeBottom(image):
    height = image.shape[0]
    width = image.shape[1]
    xPositions = []
    for i in range(width):
        if (image[height - 1, i] == 255):
            print(image[height - 1,i])
            print("found")
            xPositions.append(i)
    print("Bottom position 1: " + str(xPositions[0]))
    print("Bottom position 2: " + str(xPositions[1]))
    return xPositions

def TROI(image):
    xBottomPositions = getPointsOfChangeBottom(image)

    pixelOffset = 10

    TYPosL = []
    TYPosR = []

    for i in range (image.shape[0] - 1, -1, -1):
        #left side
        if(image[i, xBottomPositions[0] - pixelOffset] == 255):
            print("found left y pos: " + str(i))
            TYPosL.append(i)
        #right side
        if(image[i, xBottomPositions[1] + pixelOffset] == 255):
            print("found right y pos: " + str(i))
            TYPosR.append(i)

    print("left pos: " + str(TYPosL))
    print("right pos: " + str(TYPosR))

    TMiddle = int((sum(TYPosR) + sum(TYPosL))/ float(len(TYPosR) + len(TYPosL)))
    TXPos = []

    for i in range (image.shape[1]):
        if (image[TMiddle, i] == 255):
            print("found  x pos: " + str(i))
            TXPos.append(i)
    print("x pos: " + str(TXPos))

    rectangle = cv2.rectangle(image, (TXPos[0], TYPosL[0]), (TXPos[1], TYPosR[1]), (255, 255, 255), -1)

    return rectangle


def main():
    print("Hello World")
    image = cv2.imread("images/t-middle.png")

    cv2.imshow("test", image)
    cv2.waitKey(0)

    laneImage = np.copy(image)

    # changes image
    cannyImage = canny(laneImage)

    cv2.imshow("test", cannyImage)
    cv2.waitKey(0)

    foundT = TROI(cannyImage)

    cv2.imshow("test", foundT)
    cv2.waitKey(0)

main()