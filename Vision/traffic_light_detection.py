import cv2
import numpy as np

H_SAT = 500
L_SAT = 150 #150
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
    def hsv_conversion(self, image):
        return cv2.cvtColor(image.copy(), cv2.COLOR_BGR2HSV)
    def gray_conversion(self, image):
        return cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY)
    def color_filtering(self, image, roi=None, print_enable=False):
        self.height, self.width = image.shape[:2]
        hsv_image = self.hsv_conversion(image)
        h, s, v = cv2.split(hsv_image)

        s_cond = (s > L_SAT) #& (s < H_SAT)
        if roi is RED:
            h_cond = (h < HUE_THRESHOLD[roi][0]) | (h > HUE_THRESHOLD[roi][1])
        else:
            h_cond = (h > HUE_THRESHOLD[roi][0]) & (h < HUE_THRESHOLD[roi][1])

        v[~h_cond], v[~s_cond] = 0, 0
        hsv_image = cv2.merge([h, s, v])
        result = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)

        if print_enable:
            cv2.imshow('colour filtered', result)

        return result
    def gaussian_blurring(self, image, kernel_size=(None, None)):
        return cv2.GaussianBlur(image.copy(), kernel_size, 0)
    def hough_transform(self, image, rho=None, theta=None, threshold=None, mll=None, mlg=None, mode="lineP"):
        if mode == "line":
            return cv2.HoughLines(image.copy(), rho, theta, threshold)
        elif mode == "lineP":
            return cv2.HoughLinesP(image.copy(), rho, theta, threshold, lines=np.array([]),
                                   minLineLength=mll, maxLineGap=mlg)
        elif mode == "circle":
            return cv2.HoughCircles(image.copy(), cv2.HOUGH_GRADIENT, dp=1, minDist=80,
                                    param1=200, param2=10, minRadius=40, maxRadius=100)
    def traffic_detection(self, image, sample=0, mode="circle", print_enable=False):
        self.height, self.width = image.shape[:2]
        result = None
        replica = image.copy()
        roi = image[0:int(self.height), 0:int(self.width)]
        for color in (RED, YELLOW, GREEN):
            extract = self.color_filtering(roi, roi=color, print_enable=True)
            gray = self.gray_conversion(extract)
            circles = self.hough_transform(gray, mode=mode)
            if circles is not None:
                for circle in circles[0]:
                    center, count = (int(circle[0]), int(circle[1])), 0

                    hsv_image = self.hsv_conversion(image)
                    h, s, v = cv2.split(hsv_image)

                    # Searching the surrounding pixels
                    for res in range(sample):
                        x, y = int(center[1] - sample / 2), int(center[0] - sample / 2)
                        s_cond = (s[x][y] > L_SAT) #& (s[x][y] < H_SAT)
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

    # UNUS MADED
    def preprocess(self, image):
        region_of_interest_vertices = np.array(
            [[(0, self.height), (self.width * (2 / 12), self.height * (7 / 12)),
              (self.width * (10/ 12), self.height * (7 / 12)), (self.width, self.height)]],
            dtype=np.int32) ### FIX ME

        gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        hist = cv2.equalizeHist(gray_image)
        open = self.morphology(hist, (5, 5), mode="opening")
        close = self.morphology(open, (11, 11), mode="closing")
        blur_image = cv2.GaussianBlur(close, (5, 5), 0)
        canny_image = cv2.Canny(blur_image, 130, 250)
        cropped_image = self.region_of_interest(canny_image, np.array([region_of_interest_vertices], np.int32), )

        return cropped_image
    def color_detection(frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        green_lower = np.array([40, 40, 40])
        green_upper = np.array([70, 255, 255])
        green_mask = cv2.inRange(hsv, green_lower, green_upper)
        green = cv2.bitwise_and(frame, frame, mask=green_mask)
        red_lower = np.array([0, 50, 50])
        red_upper = np.array([10, 255, 255])
        red_mask = cv2.inRange(hsv, red_lower, red_upper)
        red = cv2.bitwise_and(frame, frame, mask=red_mask)

        if np.count_nonzero(green_mask) > np.count_nonzero(red_mask):
            return 'go'  # go
        elif np.count_nonzero(red_mask) > np.count_nonzero(green_mask):
            return 'stop'