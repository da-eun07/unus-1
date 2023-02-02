import sys
import cv2
import numpy as np
np.set_printoptions(threshold=sys.maxsize, linewidth=150)

SATURATION = 150

class libLANE(object):
    def __init__(self):
        self.height = 0
        self.width = 0
        self.min_y = 0
        self.max_y = 0
        self.match_mask_color = 255
        self.poly_data_r = None
        self.poly_data_l = None
        self.poly_data_c = None
        self.line_bool_r = False
        self.line_bool_l = False
    def region_of_interest(self, image, vertices):
        mask = np.zeros_like(image)
        if len(image.shape) > 2:
            self.match_mask_color = (255,255,255)
        cv2.fillPoly(mask, vertices, self.match_mask_color)
        masked_image = cv2.bitwise_and(image, mask)
        return masked_image
    def weighted_img(self, image, initial_img, α=1, β=1., λ=0.):
        return cv2.addWeighted(initial_img, α, image, β, λ)
    def hough_transform(self, image, rho=None, theta=None, threshold=None, mll=None, mlg=None, mode="lineP"):
        if mode == "line":
            return cv2.HoughLines(image.copy(), rho, theta, threshold)
        elif mode == "lineP":
            return cv2.HoughLinesP(image.copy(), rho, theta, threshold, lines=np.array([]),
                                   minLineLength=mll, maxLineGap=mlg)
        elif mode == "circle":
            return cv2.HoughCircles(image.copy(), cv2.HOUGH_GRADIENT, dp=1, minDist=80,
                                    param1=200, param2=10, minRadius=40, maxRadius=100)
    def morphology(self, image, kernel_size=(None, None), mode="opening"):
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)

        if mode == "opening":
            dst = cv2.erode(image.copy(), kernel)
            return cv2.dilate(dst, kernel)
        elif mode == "closing":
            dst = cv2.dilate(image.copy(), kernel)
            return cv2.erode(dst, kernel)
        elif mode == "gradient":
            return cv2.morphologyEx(image.copy(), cv2.MORPH_GRADIENT, kernel)
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
    def preprocess2(self, image, roi='a'):
        a_roi = np.array(
            [[(0, self.height - 70), (0, 0),
              (self.width, 0), (self.width, self.height - 70)]],
            dtype=np.int32)
        r_roi = np.array(
            [[(self.width / 2 - 140, self.height - 50), (self.width / 2 - 140, 0),
              (self.width, 0), (self.width, self.height - 50)]],
            dtype=np.int32)
        l_roi = np.array(
            [[(0, self.height - 50), (0, 0),
              (self.width /2 - 140, self.height - 50), (self.width /2 - 140, 0)]],
            dtype=np.int32)
        side_roi = np.array(
            [[(200, self.height), (200, 0),
              (self.width, 0), (self.width, self.height)]],
            dtype=np.int32)

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        white = cv2.inRange(hsv, (0, 0, 160), (180, 255, 255))  ### FIX ME
        green_mask = cv2.inRange(hsv, (30, 20, 23), (70, 255, 255))  ### FIX ME
        green_imask = green_mask > 0
        white[green_imask] = 0
        blur_image = cv2.GaussianBlur(white, (5, 5), 0)
        open = self.morphology(blur_image, (4, 4), mode="opening")
        close = self.morphology(open, (8, 8), mode="closing")
        canny_image = cv2.Canny(close, 130, 250)
        if roi == 'a' :
            cropped_image = self.region_of_interest(canny_image, np.array([a_roi], np.int32))
        elif roi == 'r':
            cropped_image = self.region_of_interest(canny_image, np.array([r_roi], np.int32))
        elif roi == 'l':
            cropped_image = self.region_of_interest(canny_image, np.array([l_roi], np.int32))
        else:
            cropped_image = self.region_of_interest(canny_image, np.array([side_roi], np.int32))
        i = cropped_image > 0
        cropped_image[i] = 255
        return white
    def preprocess3(self, image, roi='a'):
        a_roi = np.array(
            [[(0, self.height - 70), (0, 0),
              (self.width, 0), (self.width, self.height - 70)]],
            dtype=np.int32)
        r_roi = np.array(
            [[(self.width / 2 - 140, self.height - 50), (self.width / 2 - 140, 0),
              (self.width, 0), (self.width, self.height - 50)]],
            dtype=np.int32)
        l_roi = np.array(
            [[(0, self.height - 50), (0, 0),
              (self.width / 2 - 140, self.height - 50), (self.width / 2 - 140, 0)]],
            dtype=np.int32)

        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv_image)
        v_max = np.max(v)
        lower_white = np.array([25, 0, int(v_max * 0.6)])
        upper_white = np.array([130, 25, 255])
        mask = cv2.inRange(hsv_image, lower_white, upper_white)
        close = self.morphology(mask, (4, 4), mode="closing")
        open = self.morphology(close, (4, 4), mode="opening")
        blur_image = cv2.GaussianBlur(open, (3, 3), 0)
        canny_image = cv2.Canny(blur_image, 200, 400)
        if roi == 'a' :
            cropped_image = self.region_of_interest(canny_image, np.array([a_roi], np.int32))
        elif roi == 'r':
            cropped_image = self.region_of_interest(canny_image, np.array([r_roi], np.int32))
        else:
            cropped_image = self.region_of_interest(canny_image, np.array([l_roi], np.int32))
        i = cropped_image > 0
        cropped_image[i] = 255
        return cropped_image
    def draw_lines(self, image, lines, color=[0, 0, 255], thickness=7):
        line_image = np.zeros((image.shape[0],image.shape[1],3),dtype=np.uint8)
        if lines is None:
            return
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_image, (x1, y1), (x2, y2), color, thickness)
        return line_image
    def draw_poly(self, image, poly, min, max, color=[0, 255, 0], thickness=7):
        poly_image = np.zeros((image.shape[0],image.shape[1],3),dtype=np.uint8)
        for y in np.arange(min, max, 1):
            y = int(y)
            x = int(poly(y))
            cv2.line(poly_image, (x, y), (x, y), color=color, thickness=thickness)
        return poly_image
    def get_poly(self, line_y, line_x, lr, deg, weight=0.75):
        if deg == 1:
            poly_param = np.polyfit(line_y, line_x, deg=1)
        else:
            poly_param = np.polyfit(line_y, line_x, deg=2)
            if abs(poly_param[0]) > 0.0005 : ### FIX ME
                poly_param = np.polyfit(line_y, line_x, deg=1)
        if len(poly_param) == 2:
            poly_param = np.append(np.array([0]), poly_param)

        if lr == 'r':
            if self.poly_data_r is not None:
                poly_param = poly_param * (1 - weight) + self.poly_data_r * (weight)
            self.poly_data_r = poly_param
        elif lr == 'l':
            if self.poly_data_l is not None:
                poly_param = poly_param * (1 - weight) + self.poly_data_l * (weight)
            self.poly_data_l = poly_param
        else:
            if self.poly_data_c is not None:
                poly_param = poly_param * (1 - weight) + self.poly_data_c * (weight)
            self.poly_data_c = poly_param

        poly = np.poly1d(poly_param)
        return poly, poly_param

    # PLAN A : USING ABOVE CAM
    def red_center(self, image):
        self.height, self.width = image.shape[:2]
        self.min_y = 0
        self.max_y = int(self.height)
        c_lines = []
        c_lines_x = []
        c_lines_y = []
        center_line = None
        center_image = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        hsv_img = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv_img)

        s_cond = s > SATURATION
        h_cond = (h < 4) | (h > 176)

        v[~h_cond], v[~s_cond] = 0, 0
        hsv_image = cv2.merge([h, s, v])
        rgb_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)
        canny_image = cv2.Canny(rgb_image, 80, 250)

        lines = self.hough_transform(canny_image, rho=1, theta=np.pi / 180, threshold=10, mll=10, mlg=20, mode="lineP")

        if lines is not None:
            for line in lines:
                for x1, y1, x2, y2 in line:
                    slope = (y2 - y1) / (x2 - x1)
                    if np.abs(slope) < 0.5:  # stop line
                        continue
                    else:
                        c_lines.append([[x1, y1, x2, y2]])
                        c_lines_x.extend([x1, x2])
                        c_lines_y.extend([y1, y2])

            center_line, _ = self.get_poly(c_lines_y, c_lines_x, 'c', deg=1, )

            x_start = int(center_line(0))
            x_end = int(center_line(self.height))
            center_image = self.draw_lines(image, [[[x_start, 0, x_end, self.height], ]], color=[255, 0, 0],
                                           thickness=7, )

        return center_line, center_image
    def right_lane(self, image, deg):
        self.height, self.width = image.shape[:2]
        self.min_y = 0
        self.max_y = int(self.height)
        right_line_x = []
        right_line_y = []
        poly_r = None
        poly_image_r = np.zeros((image.shape[0],image.shape[1],3),dtype=np.uint8)

        right_image = self.preprocess2(image, "r")
        lines_r = self.hough_transform(right_image, rho=1, theta=np.pi / 180, threshold=10, mll=10, mlg=20, mode="lineP")

        if lines_r is not None:
            self.line_bool_r = True
            for line in lines_r:
                for x1, y1, x2, y2 in line:
                    slope = (y2 - y1) / (x2 - x1)
                    if np.abs(slope) < 0.5:  # stop line
                        continue
                    if slope <= 0:
                        continue
                    else:
                        right_line_x.extend([x1, x2])
                        right_line_y.extend([y1, y2])

            if len(right_line_y) != 0:
                # Drawing POLY (deg=2)
                if deg == 2:
                    poly_r, _ = self.get_poly(right_line_y, right_line_x, 'r', deg, 0.75)
                    poly_image_r = self.draw_poly(image, poly_r, self.min_y, self.max_y, color=[0, 255, 0], thickness=7)

                # Drawing LINE (deg=1)
                else:
                    poly_line_r, _ = self.get_poly(right_line_y, right_line_x, 'r', deg, 0.75)
                    x_start_r = int(poly_line_r(self.max_y))
                    x_end_r = int(poly_line_r(self.min_y))
                    poly_image_r = self.draw_lines(image, [[[x_start_r, self.max_y, x_end_r, self.min_y], ]], color=[0, 255, 0], thickness=7, )


        if self.line_bool_r is False:
            return poly_r, poly_image_r
        else:
            return poly_r, poly_image_r
    def left_lane(self, image, deg):
        self.height, self.width = image.shape[:2]
        self.min_y = 0
        self.max_y = int(self.height)
        left_line_x = []
        left_line_y = []
        poly_l = None
        poly_image_l = np.zeros((image.shape[0],image.shape[1],3),dtype=np.uint8)

        left_image = self.preprocess2(image, "l")
        lines_l = self.hough_transform(left_image, rho=1, theta=np.pi / 180, threshold=10, mll=10, mlg=20, mode="lineP")

        if lines_l is not None:
            self.line_bool_l = True
            for line in lines_l:
                for x1, y1, x2, y2 in line:
                    slope = (y2 - y1) / (x2 - x1)
                    if np.abs(slope) < 0.5:  # stop line
                        continue
                    if slope <= 0:
                        left_line_x.extend([x1, x2])
                        left_line_y.extend([y1, y2])

            if len(left_line_y) != 0:
                # Drawing POLY (deg=2)
                if deg == 2:
                    poly_l, _ = self.get_poly(left_line_y, left_line_x, 'l', deg, weight=0.9)
                    poly_image_l = self.draw_poly(image, poly_l, self.min_y, self.max_y, color=[255, 0, 0], thickness=7)

                # Drawing LINE (deg=1)
                else:
                    poly_line_l, _ = self.get_poly(left_line_y, left_line_x, 'l', deg, weight=0.9)

                    x_start_l = int(poly_line_l(self.max_y))
                    x_end_l = int(poly_line_l(self.min_y))
                    poly_image_l = self.draw_lines(image, [[[x_start_l, self.max_y, x_end_l, self.min_y], ]], color=[255, 0, 0], thickness=7, )
        if self.line_bool_r is False:
            return poly_l, poly_image_l
        else:
            return poly_l, poly_image_l
    def add_lane(self, image, deg):
        self.height, self.width = image.shape[:2]
        self.min_y = 0
        self.max_y = int(self.height)

        r_b, right = self.right_lane(image, deg)
        # l_b, left = self.left_lane(image, deg)
        # center_line, center = self.red_center(image)
        center = self.draw_lines(image, [[[823, self.max_y, 775, self.min_y], ]], color=[0, 0, 255], thickness=7, )
        #lane = right + left
        lane_center = self.weighted_img(right, center, 1.0, 1.0, 0)
        result = self.weighted_img(lane_center, image, 0.8, 1.0, 0)

        return result

    # PLAN B : USING SIDE CAM
    def steering_poly(self, poly, param):
        hfs = poly(self.width/2)
        if hfs < self.height * (2/5):
            steer = 'right'
        elif hfs > self.height * (3/5):
            steer = 'left'
        else:
            if param[1] > 0.12: ### FIX ME
                steer = 'right'
            elif param[1] < -0.12:
                steer = 'left'
            else:
                steer = 'forward'
        # print("steer by poly")
        return steer
    def steering_notp(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        green_mask = cv2.inRange(hsv, (30, 20, 23), (70, 255, 255))  ### FIX ME
        gray_mask = cv2.inRange(hsv, (0, 0, 0), (180, 255, 150)) ### FIX ME
        green = np.count_nonzero(green_mask==255)
        gray = np.count_nonzero(gray_mask==255)
        if green >= gray:
            steer = 'left'
        else:
            steer = 'right'
        # print("steer by colour")
        return steer
    def hough_lane(self, image):
        self.height, self.width = image.shape[:2]

        pre_image = self.preprocess2(image, 'a')
        lines = self.hough_transform(pre_image, rho=1, theta=np.pi/180, threshold=10, mll=10, mlg=20, mode="lineP")

        if lines is None:
            hough_result = image
        else:
            line_image = self.draw_lines(image, lines, color=[0, 0, 255], thickness=15)
            hough_result = self.weighted_img(line_image, image, 0.8, 1.0, 0)

        return lines, hough_result
    def side_lane(self, image):
        lines, hough = self.hough_lane(image)
        line_x = []
        line_y = []
        # side_result = np.zeros((image.shape[0], image.shape[1], 3), dtype=np.uint8)
        c_steer = 'forward'

        if lines is not None:
            for line in lines:
                for x1, y1, x2, y2 in line:
                    slope = (y2 - y1) / (x2 - x1)
                    if np.abs(slope) < 0.3: ### FIX ME
                        line_x.extend([x1, x2])
                        line_y.extend([y1, y2])

            if len(line_y) != 0:
                # DRAW LINE
                poly_line, poly_param = self.get_poly(line_x, line_y, 'l', deg=1, weight=0.2)  ### FIX ME
                # print(poly_param[1])
                c_steer = self.steering_poly(poly_line, poly_param)
                y_start = int(poly_line(0))
                y_end = int(poly_line(self.width))
                poly_image = self.draw_lines(image, [[[0, y_start, self.width, y_end], ]],
                                                       color=[255, 0, 255], thickness=15, )
                side_result = self.weighted_img(poly_image, image, 0.8, 1.0, 0)
            else:
                c_steer = self.steering_notp(image)
                side_result = image
        else:
            side_result = image

        return c_steer, side_result