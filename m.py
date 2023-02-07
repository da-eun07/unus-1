import cv2
import matplotlib.pyplot as plt

img = cv2.imread('record/06_22-03-54.jpg', -1)
plt.imshow(img)
plt.show()