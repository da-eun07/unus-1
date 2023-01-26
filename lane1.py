# -*- coding: utf-8 -*-
import cv2
import Vision.cv_util_func as cv_util
import Vision.cam_util_func as cam_util

'''
# image
lane_detection = cv_util.libLANE()
image = cv2.imread('./test_images/24_19-48-02.png')
result = lane_detection.lane(image)

cv2.imshow('result', result)
cv2.waitKey(0)

'''
'''
# video
cap = cv2.VideoCapture('./test_videos/1.mp4')
lane_detection = cv_util.libLANE()

while (cap.isOpened()):
    ret, image = cap.read()
    #hough = lane_detection.hough_lane(image)
    #right = lane_detection.preprocess2(image, 'r')
    #left = lane_detection.preprocess2(image, 'l')
    add = lane_detection.add_lane(image, 2)

    #cv2.imshow('hough', hough)
    #cv2.imshow('left', left)
    #cv2.imshow('right', right)
    cv2.imshow('add', add)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release
cap.release()
cv2.destroyAllWindows()
'''


# cam
cam = cam_util.libCAMERA()
ch0, ch1 = cam.initial_setting(cam0port=1, cam1port=2, capnum=2)
lane_detection = cv_util.libLANE()

while True:
    _, frame0, _, frame1 = cam.camera_read(ch0, ch1)
    cam.image_show(frame0, frame1)

    add0 = lane_detection.add_lane(frame0, 2) ### set ROI and parameter
    add1 = lane_detection.add_lane(frame1, 2)
    cv2.imshow('add', add0)
    cv2.imshow('add1',add1)
    if cam.loop_break():
        break

# Release
cv2.destroyAllWindows()
