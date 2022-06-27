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

def findROI(image):
    height = image.shape[0]
    width = image.shape[1]

    xTopPositions = getPointsOfChangeTop(image)
    xBottomPositions = getPointsOfChangeBottom(image)

    print(xBottomPositions[0])
    print(xTopPositions[1])

    if(xBottomPositions[0] > xTopPositions[0]):
        rectangle = cv2.rectangle(image, (xBottomPositions[1], height), (xTopPositions[0], 0), (255, 255, 255), -1)

    else:
        rectangle = cv2.rectangle(image, (xBottomPositions[0], height), (xTopPositions[1], 0), (255, 255, 255), -1)

    return rectangle

def findAngle(image, xTopPositions, xBottomPositions):
    height = image.shape[0]
    deltaX = xTopPositions[0] - xBottomPositions[0]


    if (deltaX == 0):
        print("straight")

        return imageText(image, "Image is Straight")

    m = (0 - height)/(xTopPositions[0] - xBottomPositions[0])

    theta = -math.atan(m) * (180.0/math.pi)

    if(m <= 0):
        print("(slope less than 0) angle: " + str(theta))

        return imageText(image, str(round(theta,3)) + " degree angle")

    else:
        print("angle: " + str(theta))

        return imageText(image, str(round(theta, 3)) + " degree angle")


def main():
    print("Hello World")
    image = cv2.imread("images/straight.png")

    cv2.imshow("test", image)
    cv2.waitKey(0)

    laneImage = np.copy(image)

    # changes image
    cannyImage = canny(laneImage)

    cv2.imshow("test", cannyImage)
    cv2.waitKey(0)

    xTopPositions = getPointsOfChangeTop(cannyImage)
    xBottomPositions = getPointsOfChangeBottom(cannyImage)

    # plt just shows it on a graph with some nicer UI features
    #plt.imshow(cannyImage)
    #plt.show()

    regionOfInterest = findROI(cannyImage)
    cv2.imshow("result", regionOfInterest)
    cv2.waitKey(0)

    angleImage = findAngle(laneImage, xTopPositions, xBottomPositions)

    cv2.imshow("angle", angleImage)
    cv2.waitKey(0)


main()