import Vision.traffic_light_detection as tf_util
import Vision.cam_util_func as cam_util
import Vision.lane_detection as lane_util
import cv2
'''
# 1
# image
lane = lane_util.libLANE()
tf = tf_util.libTRAFFIC()
image = cv2.imread('./test_images/traffic.png')
# cv2.imshow('im', image)
color = tf.traffic_detection(image, sample=16, print_enable=True)
cv2.waitKey(0)
'''

# 2
# webcam
tf = tf_util.libTRAFFIC()
cam = cam_util.libCAMERA()
ch0, ch1 = cam.initial_setting_480(cam0port=1, cam1port=0, capnum=2) ### For MAC OS
# ch0, ch1 = cam.initial_setting_window(cam0port=0, cam1port=1, capnum=1) ### For WINDOW OS

while True:
    _, frame0, _, frame1 = cam.camera_read(ch0, ch1)
    cam.image_show(frame1)
    color = tf.traffic_detection(frame1, sample=5, print_enable=True) #16

    if cam.loop_break():
        break
    if cam.capture(frame1):
        continue

# Release
cv2.destroyAllWindows()
