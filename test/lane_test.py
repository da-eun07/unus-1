# -*- coding: utf-8 -*-
import cv2
import Vision.lane_detection as lane_util
import Vision.cam_util_func as cam_util
import Vision.bird_eye_view as bev

'''
# 1
# image
lane_detection = lane_util.libLANE()
image = cv2.imread('./record/01_16-06-34.jpg')
# cv2.imshow('im', image)

_, pre = lane_detection.hough_lane(image)
cv2.imshow('hough', pre)
steer, poly = lane_detection.side_lane(image)
cv2.imshow('p',poly)
print(steer)

cv2.waitKey(0)

'''

'''
# 2
# video
cap = cv2.VideoCapture('./test_videos/2.mp4')
lane_detection = lane_util.libLANE()

while (cap.isOpened()):
    ret, image = cap.read()
    #hough = lane_detection.hough_lane(image)
    right = lane_detection.preprocess2(image, 'r')
    _, right_line = lane_detection.right_lane(image, 2)
    #left = lane_detection.preprocess2(image, 'l')
    add = lane_detection.add_lane(image, 2)

    #cv2.imshow('hough', hough)
    #cv2.imshow('left', left)
    cv2.imshow('righta', right_line)
    cv2.imshow('right', right)
    cv2.imshow('add', add)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release
cap.release()
cv2.destroyAllWindows()

'''


# 3
# cam

cam = cam_util.libCAMERA()
ch0, ch1 = cam.initial_setting_1080(cam0port=0, cam1port=0, capnum=1) ### For MAC OS
# ch0, ch1 = cam.initial_setting_window(cam0port=0, cam1port=1, capnum=1) ### For WINDOW OS
lane_detection = lane_util.libLANE()

while True:
    _, frame0= cam.camera_read(ch0)
    cam.image_show(frame0)
    t_frame0 = bev.bev(frame0)
    cv2.imshow('t', t_frame0)
    white = lane_detection.preprocess2(t_frame0, 'a')
    cv2.imshow('hough', white)
    #_, right = lane_detection.right_lane(frame0, 2)
    #cv2.imshow('p', right)
    lane = lane_detection.add_lane(t_frame0, 2)
    cv2.imshow('l', lane)

    if cam.loop_break():
        break
    if cam.capture(frame0):
        continue

# Release
cv2.destroyAllWindows()
