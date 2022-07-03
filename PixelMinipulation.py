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

    copyImage = np.copy(image)
    height = copyImage.shape[0]
    width = copyImage.shape[1]

    xTopPositions = getPointsOfChangeTop(copyImage)
    xBottomPositions = getPointsOfChangeBottom(copyImage)

    print(xBottomPositions[0])
    print(xTopPositions[1])

    if(xBottomPositions[0] > xTopPositions[0]):
        rectangle = cv2.rectangle(copyImage, (xBottomPositions[1], height), (xTopPositions[0], 0), (255, 255, 255), -1)

    else:
        rectangle = cv2.rectangle(copyImage, (xBottomPositions[0], height), (xTopPositions[1], 0), (255, 255, 255), -1)

    return rectangle

def findAngle(image, xTopPositions, xBottomPositions):
    copyImage = np.copy(image)

    height = copyImage.shape[0]
    deltaX = xTopPositions[0] - xBottomPositions[0]


    if (deltaX == 0):
        print("straight")

        return imageText(copyImage, "Image is Straight"), 0

    m = (0 - height)/(xTopPositions[0] - xBottomPositions[0])

    theta = -math.atan(m) * (180.0/math.pi)

    if(m <= 0):
        print("(slope less than 0) angle: " + str(theta))

        return imageText(copyImage, str(round(theta,3)) + " degree angle"), theta

    else:
        print("angle: " + str(theta))

        return imageText(copyImage, str(round(theta, 3)) + " degree angle"), theta


def findPos(image):

    pointsOfChangeTop = getPointsOfChangeTop(image)
    print(pointsOfChangeTop)
    pointsOfChangeBottom = getPointsOfChangeBottom(image)
    print(pointsOfChangeBottom)
    angleImage, angle = findAngle(image, getPointsOfChangeTop(image), getPointsOfChangeBottom(image))

    if(angle == 0):
        topMedianPos = int(float(pointsOfChangeTop[1] + pointsOfChangeTop[0])/2)
        print(topMedianPos)
        botMedianPos = int(float(pointsOfChangeBottom[1] + pointsOfChangeBottom[0])/2)
        print(botMedianPos)
        averageMedian = int(float(topMedianPos + botMedianPos)/2)
        print(averageMedian)

        if(220 <= averageMedian and averageMedian <= 320):
            print("position does not need to be changed")
            print("line position is "  + str(abs(int((float(image.shape[1]/2))) - averageMedian)) + " pixels away from the median line")
        else:
            if(averageMedian < (image.shape[1]/2)):
                print("line position is " + str(abs(int((float(image.shape[1]/2))) - averageMedian)) + " pixels to the left of the median line")
            else:
                print("line position is " + str(abs(int((float(image.shape[1]/2))) - averageMedian)) + " pixels to the right of the median line")

    else:
        topMedianPos = int(float(pointsOfChangeTop[1] + pointsOfChangeTop[0]) / 2)
        print(topMedianPos)
        botMedianPos = int(float(pointsOfChangeBottom[1] + pointsOfChangeBottom[0]) / 2)
        print(botMedianPos)
        averageMedian = int(float(topMedianPos + botMedianPos) / 2)
        print(averageMedian)

        if (220 <= averageMedian and averageMedian <= 320):
            print("position does not need to be changed, angle does need to be changed")
            print("line positionis " + str(abs(int((float(image.shape[1]/2))) - averageMedian)) + " pixels away from the median line")
            print("angle " + str(angle))
        else:
            print("position and angle need to be changed")
            if(averageMedian < (image.shape[1]/2)):
                print("line position is " + str(abs(int((float(image.shape[1]/2))) - averageMedian)) + " pixels to the left of the median line")
                print("angle " + str(angle))
            else:
                print("line position is " + str(abs(int((float(image.shape[1]/2))) - averageMedian)) + " pixels to the right of the median line")
                print("angle " + str(angle))

def main():
    print("Hello World")
    image = cv2.imread("images/line_left.png")

    cv2.imshow("test", image)
    cv2.waitKey(0)

    laneImage = np.copy(image)

    # changes image
    cannyImage = canny(laneImage)

    cv2.imshow("test", cannyImage)
    cv2.waitKey(0)

    print("step 2")
    xTopPositions = getPointsOfChangeTop(cannyImage)
    xBottomPositions = getPointsOfChangeBottom(cannyImage)

    # plt just shows it on a graph with some nicer UI features
    #plt.imshow(cannyImage)
    #plt.show()

    print("step 3")
    regionOfInterest = findROI(cannyImage)
    cv2.imshow("result", regionOfInterest)
    cv2.waitKey(0)

    print("step 4")
    angleImage, angle = findAngle(cannyImage, xTopPositions, xBottomPositions)

    cv2.imshow("angle", angleImage)


    print("step 5")
    findPos(cannyImage)

    cv2.waitKey(0)


main()

"""
line is off to the left but they are not perfect

two senarios where we need to make changes:
if the angle is completly off and we are centered / we are too the left of the image we have a problem
if the angle is fine but they are but they are not near the pool line

angle does not matter if the position is way off
if the position is fine but angle is way off, fix the angle
"""

"""
haptic feeback
think in binary:
tap on right or left shouolder based on position(if position off: touch, it angle is off (more than 5 degrees) and they are on the line: fix angle a liitle)

if(right): touch left sholder
elif(left): tought right sholder
else:(straight) fix your corection angle to straighten out
"""
"""
fix tolerances for:
    angle: be absolute
    position: get width of the line
    * as depth increases your width will shrink
    eg:
        lane line is 8 inches: lane is 80 inches  (ratio 1:10)
    base of width
"""
"""
fix ROI
if we start off wrong and only have one canny image
"""
"""
rasberrypi
find out the OS used
find out how to download 'how to install raspbian on raspberry pi'
"""
"""
adafruit.com for how to use motors and camera
"""