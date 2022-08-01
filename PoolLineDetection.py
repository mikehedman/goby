import cv2
import numpy as np
import matplotlib.pyplot as plt
import math

# saves time if i want to wright text on images
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


#used to find coordinates of change in the bottom of the image
def getPointsOfChangeTop(image):
    width = image.shape[1]
    xPositions = []
    for i in range (width):
        if(image[0, i] == 255):
            #print("found")
            xPositions.append(i)
    if(len(xPositions) == 0):
        return xPositions
    #print("Top position 1: " + str(xPositions[0]))
    #print("Top position 2: " + str(xPositions[1]))
    return xPositions

#used to find coordinates of change in the bottom of the image
def getPointsOfChangeBottom(image):
    height = image.shape[0]
    width = image.shape[1]
    xPositions = []
    for i in range(width):
        if (image[height - 1, i] == 255):
            #print(image[height - 1,i])
            #print("found")
            xPositions.append(i)
    #print("Bottom position 1: " + str(xPositions[0]))
    #print("Bottom position 2: " + str(xPositions[1]))
    return xPositions

#finds the ROI for image with a line in it.
def lineROI(image):

    copyImage = np.copy(image)

    height = copyImage.shape[0]
    width = copyImage.shape[1]

    #find the top coordinates and bottom coordintes of the pool line
    xTopPositions = getPointsOfChangeTop(copyImage)
    xBottomPositions = getPointsOfChangeBottom(copyImage)

    #print(xBottomPositions[0])
    #print(xTopPositions[1])

    #if our line is angled depending on the coordinates found in the image we might have to inverse coordinates in order for the ROI to encompass the whole line
    if(xBottomPositions[0] > xTopPositions[0]):
        rectangle = cv2.rectangle(copyImage, (xBottomPositions[1], height), (xTopPositions[0], 0), (255, 255, 255), -1)

    else:
        rectangle = cv2.rectangle(copyImage, (xBottomPositions[0], height), (xTopPositions[1], 0), (255, 255, 255), -1)

    return rectangle

#finds the ROI for image with a T in it
def TROI(image):
    tImage = np.copy(image)

    # find the top coordinates and bottom coordintes of the pool line
    xBottomPositions = getPointsOfChangeBottom(tImage)
    xTopPositions = getPointsOfChangeTop(tImage)

    #canny Images for crosses can become blury at corners, we offset the distance from the cornors to find the accurate pixel coordienate
    pixelOffset = 10

    #Takes the Y values that are white of a canny image on the left and right side of the T
    TYPosL = []
    TYPosR = []

    # if there is white on the top part of the image we know that the image is not a T
    # we return an image that states there is no T and a false boolean value
    if(len(xTopPositions) > 0):
        return imageText(tImage, "No T"), False

    # if there are no white values on the top of the image we execute the algorithm to find the t
    for i in range (tImage.shape[0] - 1, -1, -1):
        #finds y values on left side
        if(tImage[i, xBottomPositions[0] - pixelOffset] == 255):
            #print("found left y pos: " + str(i))
            TYPosL.append(i)
        #finds y values on right side
        if(tImage[i, xBottomPositions[1] + pixelOffset] == 255):
            #print("found right y pos: " + str(i))
            TYPosR.append(i)

    #print("left pos: " + str(TYPosL))
    #print("right pos: " + str(TYPosR))

    #Given the top and bottom of the T we can find the median y position and then find the x positions of the T
    TMiddle = int((sum(TYPosR) + sum(TYPosL))/ float(len(TYPosR) + len(TYPosL)))

    #Stores X positions in this array
    TXPos = []

    #finds X positions
    for i in range (tImage.shape[1]):
        if (image[TMiddle, i] == 255):
            #print("found  x pos: " + str(i))
            TXPos.append(i)
    #print("x pos: " + str(TXPos))

    #creates ROI given the coordinates of the T
    rectangle = cv2.rectangle(tImage, (TXPos[0], TYPosL[0]), (TXPos[1], TYPosR[1]), (255, 255, 255), -1)

    # the T is low enough we tell the person to stop swimming
    if (TYPosR[0] > 100 and TYPosL[0] > 100):
        return imageText(rectangle, "STOP"), True

    return rectangle, True

#finds the angle of a line
def findAngle(image, xTopPositions, xBottomPositions):
    copyImage = np.copy(image)

    # Use formula arctan(y1-y2/x1-x2) * pi/180 to find the angle of the line
    height = copyImage.shape[0]
    deltaX = xTopPositions[0] - xBottomPositions[0]

    # if the change in x is 0 this means that the line is straight also we can't divide by 0
    # in the futre will create a range for delta X instead of just 0
    if (deltaX == 0):
        #print("straight")

        #returns image and angle
        return imageText(copyImage, "Image is Straight"), 0

    # calculates slope
    m = (0 - height)/(xTopPositions[0] - xBottomPositions[0])

    #finds angle
    theta = -math.atan(m) * (180.0/math.pi)

    # if the slope is  negative: left side
    if(m <= 0):
        #print("(slope less than 0) angle: " + str(theta))

        return imageText(copyImage, str(round(theta,3)) + " degree angle"), theta

    # if the slope is posative: right side
    else:
        #print("angle: " + str(theta))

        return imageText(copyImage, str(round(theta, 3)) + " degree angle"), theta


def findPos(image):

    #find top and bottom positions and angle
    pointsOfChangeTop = getPointsOfChangeTop(image)
    print(pointsOfChangeTop)
    pointsOfChangeBottom = getPointsOfChangeBottom(image)
    print(pointsOfChangeBottom)
    angleImage, angle = findAngle(image, getPointsOfChangeTop(image), getPointsOfChangeBottom(image))

    # if picture is straight
    if(angle == 0):
        # find the  median position of the line
        topMedianPos = int(float(pointsOfChangeTop[1] + pointsOfChangeTop[0])/2)
        #print(topMedianPos)
        botMedianPos = int(float(pointsOfChangeBottom[1] + pointsOfChangeBottom[0])/2)
        #print(botMedianPos)
        averageMedian = int(float(topMedianPos + botMedianPos)/2)
        #print(averageMedian)

        # if that matches the range then say that we are essentially in the right position
        if(220 <= averageMedian and averageMedian <= 320):
            print("position does not need to be changed")
            print("line position is "  + str(abs(int((float(image.shape[1]/2))) - averageMedian)) + " pixels away from the median line")
        # if it is not in the range we state wheter line is left or right of where we need to be
        else:
            if(averageMedian < (image.shape[1]/2)):
                print("line position is " + str(abs(int((float(image.shape[1]/2))) - averageMedian)) + " pixels to the left of the median line")
            else:
                print("line position is " + str(abs(int((float(image.shape[1]/2))) - averageMedian)) + " pixels to the right of the median line")

    # if the image is angled
    else:
        topMedianPos = int(float(pointsOfChangeTop[1] + pointsOfChangeTop[0]) / 2)
        #print(topMedianPos)
        botMedianPos = int(float(pointsOfChangeBottom[1] + pointsOfChangeBottom[0]) / 2)
        #print(botMedianPos)
        averageMedian = int(float(topMedianPos + botMedianPos) / 2)
        #print(averageMedian)

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
    # Get the image and make it canny
    images = ["images/angle_left_top.png","images/angle_right_top.png","images/line_left.png","images/line_right.png","images/straight.png","images/straight-faded.png","images/t-middle.png", "images/t-past.png", "images/t-far.png"]
    for i in range (len(images) - 1):
        print("Step 1")
        image = cv2.imread(images[i])

        cv2.imshow("test", image)
        cv2.waitKey(0)

        laneImage = np.copy(image)

        # changes image
        cannyImage = canny(laneImage)

        #cv2.imshow("test", cannyImage)
        #cv2.waitKey(0)

        # Check if image is t or straight
        print("Step 2")

        tImage, isT = TROI(cannyImage)

        # Need to integrate the find position and find angle function into T-Shaped images
        if (isT):
            print("Image is T")
            cv2.imshow("T-Shape Image", tImage)
            cv2.waitKey(0)

        # if the image is a line and not a t-shape, we will find the angle of the image and then find the position of the line relative to the center of the image

        else:
            # little bit unessary will take out later and add it to the @findAngle funtion instead of using as parameters
            xTopPositions = getPointsOfChangeTop(cannyImage)
            xBottomPositions = getPointsOfChangeBottom(cannyImage)

            # plt just shows it on a graph with some nicer UI features
            # plt.imshow(cannyImage)
            # plt.show()

            print("step 3")
            # find ROI of a line
            regionOfInterest = lineROI(cannyImage)

            # show results
            #cv2.imshow("result", regionOfInterest)
            cv2.waitKey(0)

            print("step 4")
            # finds angle of line
            angleImage, angle = findAngle(cannyImage, xTopPositions, xBottomPositions)

            # show results
            cv2.imshow("angle", angleImage)
            cv2.waitKey(0)

            print("step 5")
            # find positions
            findPos(cannyImage)
            # could show analysis of position visually on the image, but is kind of unnecessary and messy


main()

#Get it to work