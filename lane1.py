# -*- coding: utf-8 -*-
import cv2
import Vision.cv_util_func as cv_util
'''
# image
lane_detection = cv_util.libLANE()
image = cv2.imread('./test_images/solidWhiteCurve.jpg')
result = lane_detection.lane(image)

cv2.imshow('result', result)
cv2.waitKey(0)

'''
# video
cap = cv2.VideoCapture('./test_videos/solidWhiteRight.mp4')
lane_detection = cv_util.libLANE()

while (cap.isOpened()):
    ret, image = cap.read()
    result, steer = lane_detection.lane(image)

    if steer == 'r':
        print("right")
    elif steer == 'l':
        print("left")
    
    cv2.imshow('result', result)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release
cap.release()
cv2.destroyAllWindows()
