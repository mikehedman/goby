import cv2
import numpy as np
import matplotlib.pyplot as plt
import math


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


#use after canny convertion
def getPointsOfChangeTop(image):
    width = image.shape[1]
    xPositions = []
    for i in range (width):
        if(image[0, i] == 255):
            print("found")
            xPositions.append(i)
    print("Top position 1: " + str(xPositions[0]))
    print("Top position 2: " + str(xPositions[1]))
    return xPositions

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

def findRegion(image):
    height = image.shape[0]
    width = image.shape[1]

    xTopPositions = getPointsOfChangeTop(image)
    xBottomPositions = getPointsOfChangeBottom(image)


    print(xBottomPositions[0])
    print(xTopPositions[1])


    rectangle = cv2.rectangle(image, (xBottomPositions[0], height), (xTopPositions[1], 0), (255, 255, 255), -1)

    return rectangle

def findAngle(image, xTopPositions, xBottomPositions):
    height = image.shape[0]
    m = (xTopPositions[0] - xBottomPositions[0])/(0 - height)
    if(m <= 0):
        print("(if m less than 0) angle: " + str(math.atan(m)))
    else:
        print("angle: " + math.atan(m))

def main():
    print("Hello World")
    image = cv2.imread("straight.png")

    cv2.imshow("test", image)
    cv2.waitKey(0)

    laneImage = np.copy(image)

    # changes image
    cannyImage = canny(laneImage)

    cv2.imshow("test", cannyImage)
    cv2.waitKey(0)

    xTopPositions = getPointsOfChangeTop(cannyImage)
    xBottomPositions = getPointsOfChangeBottom(cannyImage)

    #plt.imshow(cannyImage)
    #plt.show()

    regionOfInterest = findRegion(cannyImage)
    cv2.imshow("result", regionOfInterest)
    cv2.waitKey(0)

    findAngle(regionOfInterest, xTopPositions, xBottomPositions)

main()