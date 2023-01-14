import math
import sys
import cv2
import numpy as np
np.set_printoptions(threshold=sys.maxsize, linewidth=150)

class libLANE(object):
    def __init__(self):
        self.height = 0
        self.width = 0
        self.min_y = 0
        self.max_y = 0
        self.match_mask_color = 255
    def region_of_interest(self, img, vertices):
        mask = np.zeros_like(img)
        if len(img.shape) > 2:
            self.match_mask_color = (255,255,255)
        cv2.fillPoly(mask, vertices, self.match_mask_color)
        masked_image = cv2.bitwise_and(img, mask)
        return masked_image
    def weighted_img(self, img, initial_img, α=1, β=1., λ=0.):
        return cv2.addWeighted(initial_img, α, img, β, λ)
    def preprocess(self, img):
        region_of_interest_vertices_1 = np.array(
            [[(50, self.height), (self.width / 2 - 45, self.height / 2 + 60),
              (self.width / 2 + 45, self.height / 2 + 60), (self.width - 50, self.height)]],
            dtype=np.int32) ### FIX ME
        region_of_interest_vertices_2 = [(0, self.height), (self.width / 2, self.height / 2),
                                         (self.width, self.height), ]

        gray_image = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        blur_image = cv2.GaussianBlur(gray_image, (3, 3), 0)
        # cannyed_image = cv2.Canny(blur_image, 100, 200)
        canny_image = cv2.Canny(blur_image, 70, 210)

        cropped_image = self.region_of_interest(canny_image, np.array([region_of_interest_vertices_1], np.int32), )

        return cropped_image
    def draw_lines(self, img, lines, color=[0, 0, 255], thickness=2):
        line_img = np.zeros((img.shape[0],img.shape[1],3),dtype=np.uint8)
        img = np.copy(img)

        if lines is None:
            return
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_img, (x1, y1), (x2, y2), color, thickness)

        # weighted_img - image overlapping
        img = self.weighted_img(line_img, img, 0.8, 1.0, 0.0)
        return img
    def draw_poly(self, img, poly_left, poly_right):
        left_img = np.zeros((img.shape[0],img.shape[1],3),dtype=np.uint8)
        right_img = np.zeros((img.shape[0],img.shape[1],3),dtype=np.uint8)
        # line_img = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
        img = np.copy(img)

        for left_y in np.arange(self.min_y, self.max_y, 1):
            left_y = int(left_y)
            left_x = int(poly_left(left_y))
            cv2.line(left_img, (left_x, left_y), (left_x, left_y), color=[255,0,0], thickness=5)
        for right_y in np.arange(self.min_y, self.max_y, 1):
            right_y = int(right_y)
            right_x = int(poly_right(right_y))
            cv2.line(right_img, (right_x, right_y), (right_x, right_y), color=[0, 255, 0], thickness=5)

        line_img = self.weighted_img(right_img, left_img)
        img = self.weighted_img(line_img, img, 0.8, 1.0, 0)
        return img
    def get_poly(self, left_line_y, left_line_x, right_line_y, right_line_x, deg):
        if deg == 1:
            poly_left_param = np.polyfit(
                left_line_y,
                left_line_x,
                deg=1
            )
            poly_right_param = np.polyfit(
                right_line_y,
                right_line_x,
                deg=1
            )
        else:
            poly_left_param = np.polyfit(
                left_line_y,
                left_line_x,
                deg=2
            )
            if abs(poly_left_param[0]) > 0.001 : ### FIX ME
                poly_left_param = np.polyfit(
                    left_line_y,
                    left_line_x,
                    deg=1
                )
            poly_right_param = np.polyfit(
                right_line_y,
                right_line_x,
                deg=2
            )
            if abs(poly_right_param[0]) > 0.001 : ### FIX ME
                poly_right_param = np.polyfit(
                    right_line_y,
                    right_line_x,
                    deg=1
                )

        poly_left = np.poly1d(poly_left_param)
        poly_right = np.poly1d(poly_right_param)

        return poly_left, poly_right
    def get_draw_center(self, img, poly_left, poly_right):
        center = []
        line_img = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
        img = np.copy(img)

        for y in np.arange(self.min_y, self.max_y, 1):
            y = int(y)
            left_x = poly_left(y)
            right_x = poly_right(y)
            cen = int((left_x + right_x) / 2)
            center.extend([cen])
            cv2.line(line_img, (cen, y), (cen, y), color=[0, 0, 255], thickness=3)

        img = self.weighted_img(line_img, img, 1.0, 1.0, 0)
        return center, img
    def steering(self, center):
        for cen in center:
            diff = int(self.width/2) - cen
            if diff < 0:
                # print("go right")
                steer = 'r'
            else:
                # print("go left")
                steer = 'l'
        return steer

    def lane(self, image):
        self.height, self.width = image.shape[:2]
        cropped_image = self.preprocess(image)
        self.min_y = int(image.shape[0] * (3 / 5))
        self.max_y = int(image.shape[0])

        lines_1 = cv2.HoughLinesP(
            cropped_image,
            rho=1,
            theta=np.pi / 180,
            threshold=30,
            lines=np.array([]),
            minLineLength=10,
            maxLineGap=20
        )
        lines_2 = cv2.HoughLinesP(
            cropped_image,
            rho=6,
            theta=np.pi / 60,
            threshold=160,
            lines=np.array([]),
            minLineLength=40,
            maxLineGap=25
        )

        left_line_x = []
        left_line_y = []
        right_line_x = []
        right_line_y = []
        stop_line_x = []
        stop_line_y = []

        for line in lines_1:
            for x1, y1, x2, y2 in line:
                slope = (y2 - y1) / (x2 - x1)
                if np.abs(slope) < 0.5: # stop line
                    stop_line_x.extend(([x1, x2]))
                    stop_line_y.extend(([y1, y2]))
                    continue
                if slope <= 0:
                    left_line_x.extend([x1, x2])
                    left_line_y.extend([y1, y2])
                else:
                    right_line_x.extend([x1, x2])
                    right_line_y.extend([y1, y2])

        if len(left_line_y) != 0 :
            poly_left, poly_right = self.get_poly(left_line_y,left_line_x,right_line_y,right_line_x,1)
            # line_image = self.draw_poly(image, poly_left, poly_right)

            center, image = self.get_draw_center(image, poly_left, poly_right)


            # Drawing deg = 1: LINE
            left_x_start = int(poly_left(self.max_y))
            left_x_end = int(poly_left(self.min_y))
            right_x_start = int(poly_right(self.max_y))
            right_x_end = int(poly_right(self.min_y))

            # LEFT LINE
            line_image_1 = self.draw_lines(
                    image,
                [[
                    [left_x_start, self.max_y, left_x_end, self.min_y],
                ]],
                color=[255,0,0],
                thickness=5,
            )
            # RIGHT LINE
            line_image = self.draw_lines(
                line_image_1,
                [[
                    [right_x_start, self.max_y, right_x_end, self.min_y],
                ]],
                color=[0,255,0],
                thickness=5,
            )

        else:
            line_image = image

        steer = self.steering(center)
        return line_image, steer