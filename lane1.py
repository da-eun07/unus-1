# -*- coding: utf-8 -*-
import cv2
import Vision.cv_util_func as cv_util
import Vision.cam_util_func as cam_util

'''
# image
lane_detection = cv_util.libLANE()
image = cv2.imread('./test_images/solidWhiteCurve.jpg')
result = lane_detection.lane(image)

cv2.imshow('result', result)
cv2.waitKey(0)

'''
# video
cap = cv2.VideoCapture('./test_videos/20_17-21-30.mp4')
lane_detection = cv_util.libLANE()

while (cap.isOpened()):
    ret, image = cap.read()
    detected = lane_detection.lane(image)
    
    cv2.imshow('result', detected)
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

    result = lane_detection.lane(frame1)

    cv2.imshow('result', result)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    # if cam.loop_break():
    #     break

# Release
cv2.destroyAllWindows()
'''