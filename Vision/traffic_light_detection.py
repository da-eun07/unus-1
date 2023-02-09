import cv2
import numpy as np

H_SAT = 255
L_SAT = 20 #150
RED, GREEN, BLUE, YELLOW = (0, 1, 2, 3)
COLOR = ("RED", "GREEN", "BLUE", "YELLOW")
HUE_THRESHOLD = ([4, 176], [40, 90], [110, 130], [15, 40])

class libTRAFFIC(object):
    def __init__(self):
        self.height, self.width, self.dim = (0, 0, 0)
    def region_of_interest(self, image, vertices):
        mask = np.zeros_like(image)
        if len(image.shape) > 2:
            self.match_mask_color = (255,255,255)
        cv2.fillPoly(mask, vertices, self.match_mask_color)
        masked_image = cv2.bitwise_and(image, mask)
        return masked_image
    def gaussian_blurring(self, image, kernel_size=(None, None)):
        return cv2.GaussianBlur(image.copy(), kernel_size, 0)
    def hough_transform(self, image, rho=None, theta=None, threshold=None, mll=None, mlg=None, mode="circle"):
        if mode == "line":
            return cv2.HoughLines(image.copy(), rho, theta, threshold)
        elif mode == "lineP":
            return cv2.HoughLinesP(image.copy(), rho, theta, threshold, lines=np.array([]),
                                   minLineLength=mll, maxLineGap=mlg)
        elif mode == "circle":
            return cv2.HoughCircles(image.copy(), cv2.HOUGH_GRADIENT, dp=1, minDist=100,
                                    param1=200, param2=10, minRadius=33, maxRadius=38)

    # UNUS MADED
    def preprocess(self, image):
        region_of_interest_vertices = np.array(
            [[(0, 100), (0, 0),
              (self.width, 0), (self.width, 100)]],
            dtype=np.int32) ### FIX ME
        blur = self.gaussian_blurring(image, (21,21))
        cropped_image = self.region_of_interest(blur, np.array([region_of_interest_vertices], np.int32), )

        return cropped_image
    def color_detection(self, image):
        # pre = self.preprocess(image)
        pre = self.gaussian_blurring(image, (27, 27))
        hsv = cv2.cvtColor(pre, cv2.COLOR_BGR2HSV)
        green_mask = cv2.inRange(hsv, np.array([60, 20, 50]), np.array([90, 255, 255]))
        green = cv2.bitwise_and(pre, pre, mask=green_mask)
        red_mask = cv2.inRange(hsv, np.array([0, 50, 50]), np.array([10, 255, 255]))
        red = cv2.bitwise_and(pre, pre, mask=red_mask)

        if np.count_nonzero(green_mask) > np.count_nonzero(red_mask):
            return 'go'
            cv2.imshow('g', green_mask)
            green_circles = self.hough_transform(green_mask, mode='circle')
            if green_circles is not None:
                return 'go'
                for circle in green_circles[0]:
                    center, count = (int(circle[0]), int(circle[1])), 0
                    result = cv2.circle(image.copy(), center, int(circle[2]), (0, 0, 255), 2)
                    # cv2.imshow('r', result)
                    return 'go'
            else:
                return 'nothing'
        elif np.count_nonzero(red_mask) > np.count_nonzero(green_mask):
            cv2.imshow('r', red_mask)
            red_circles = self.hough_transform(red_mask, mode='circle')
            if red_circles is not None:
                return 'stop'
                for circle in red_circles[0]:
                    center, count = (int(circle[0]), int(circle[1])), 0
                    result = cv2.circle(image.copy(), center, int(circle[2]), (0, 0, 255), 2)
                    # cv2.imshow('r', result)
                    return 'stop'
            else:
                return 'nothing'