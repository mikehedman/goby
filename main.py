import cv2
import numpy as np
import matplotlib.pyplot as plt
# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


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

# creates a rectangle around the region that is most important to us
# The rectangle is based of the dementions of the image and the image created through the canny function
def regionOfInterest(image):
    height = image.shape[0]
    rectangle = cv2.rectangle(image, (200, height), (300, 0), (255,255,255), -1)
    return rectangle

def main():
    # Gets image from project
    image = cv2.imread("straight.png")
    cv2.imshow("test", image)
    cv2.waitKey(0)

    laneImage = np.copy(image)

    # changes image
    cannyImage = canny(laneImage)

    #displays images
    plt.imshow(cannyImage)
    plt.show()

    cv2.imshow("result", regionOfInterest(cannyImage))
    cv2.waitKey(0)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
