import Vision.traffic_light_detection as tf_util
import cv2

tf = tf_util.libTRAFFIC()
image = cv2.imread('./test_images/traffic.png')
cv2.imshow('im', image)
color = tf.traffic_detection(image, sample=16, print_enable=True)

cv2.waitKey(0)