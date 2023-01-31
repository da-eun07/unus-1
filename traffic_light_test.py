import Vision.traffic_light_detection as tf
import cv2

image = cv2.imread('./test_images/traffic.png')
cv2.imshow('im', image)
color = tf.object_detection(image, sample=16, print_enable=True)

cv2.waitKey(0)