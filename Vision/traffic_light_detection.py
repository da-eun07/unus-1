import cv2
import numpy as np

SATURATION = 150
RED, GREEN, BLUE, YELLOW = (0, 1, 2, 3)
COLOR = ("RED", "GREEN", "BLUE", "YELLOW")
HUE_THRESHOLD = ([4, 176], [40, 80], [110, 130], [20, 40])

class libTRAFFIC(object):
    def __init__(self):
        self.capnum = 0
        self.row, self.col, self.dim = (0, 0, 0)

    def hsv_conversion(self, img):
        return cv2.cvtColor(img.copy(), cv2.COLOR_BGR2HSV)
    def gray_conversion(self, img):
        return cv2.cvtColor(img.copy(), cv2.COLOR_BGR2GRAY)
    def color_filtering(self, img, roi=None, print_enable=False):
        self.row, self.col, self.dim = img.shape

        hsv_img = self.hsv_conversion(img)
        h, s, v = cv2.split(hsv_img)

        s_cond = s > SATURATION
        if roi is RED:
            h_cond = (h < HUE_THRESHOLD[roi][0]) | (h > HUE_THRESHOLD[roi][1])
        else:
            h_cond = (h > HUE_THRESHOLD[roi][0]) & (h < HUE_THRESHOLD[roi][1])

        v[~h_cond], v[~s_cond] = 0, 0
        hsv_image = cv2.merge([h, s, v])
        result = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)

        if print_enable:
            cv2.imshow('result', result)

        return result
    def gaussian_blurring(self, img, kernel_size=(None, None)):
        return cv2.GaussianBlur(img.copy(), kernel_size, 0)
    def hough_transform(self, img, rho=None, theta=None, threshold=None, mll=None, mlg=None, mode="lineP"):
        if mode == "line":
            return cv2.HoughLines(img.copy(), rho, theta, threshold)
        elif mode == "lineP":
            return cv2.HoughLinesP(img.copy(), rho, theta, threshold, lines=np.array([]),
                                   minLineLength=mll, maxLineGap=mlg)
        elif mode == "circle":
            return cv2.HoughCircles(img.copy(), cv2.HOUGH_GRADIENT, dp=1, minDist=80,
                                    param1=200, param2=10, minRadius=40, maxRadius=100)
    def traffic_detection(self, img, sample=0, mode="circle", print_enable=False):
        result = None
        replica = img.copy()

        for color in (RED, YELLOW, GREEN):
            extract = self.color_filtering(img, roi=color, print_enable=True)
            gray = self.gray_conversion(extract)
            circles = self.hough_transform(gray, mode=mode)
            if circles is not None:
                for circle in circles[0]:
                    center, count = (int(circle[0]), int(circle[1])), 0

                    hsv_img = self.hsv_conversion(img)
                    h, s, v = cv2.split(hsv_img)

                    # Searching the surrounding pixels
                    for res in range(sample):
                        x, y = int(center[1] - sample / 2), int(center[0] - sample / 2)
                        s_cond = s[x][y] > SATURATION
                        if color is RED:
                            h_cond = (h[x][y] < HUE_THRESHOLD[color][0]) | (h[x][y] > HUE_THRESHOLD[color][1])
                            count += 1 if h_cond and s_cond else count
                        else:
                            h_cond = (h[x][y] > HUE_THRESHOLD[color][0]) & (h[x][y] < HUE_THRESHOLD[color][1])
                            count += 1 if h_cond and s_cond else count

                    if count > sample / 2:
                        result = COLOR[color]
                        cv2.circle(replica, center, int(circle[2]), (0, 0, 255), 2)

        if print_enable:
            if result is not None:
                print("Traffic Light: ", result)
            cv2.imshow('Traffic image', replica)

        return result