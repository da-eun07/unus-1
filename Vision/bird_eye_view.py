# NOT USED
import cv2 as cv2
import numpy as np

def bev(frame):
    # Corners of Top Left , Bottom Left, Top Right, Bottom Right
    tl = (790, 560)
    bl = (400, 1080)
    tr = (1520, 560)
    br = (1920, 1080)

    # Corner 포인트들 파란 점으로 표시
    # cv2.circle(frame, tl, 5, (255, 0, 0), -1)
    # cv2.circle(frame, bl, 5, (255, 0, 0), -1)
    # cv2.circle(frame, tr, 5, (255, 0, 0), -1)
    # cv2.circle(frame, br, 5, (255, 0, 0), -1)

    # Apply Geometrical Transformation
    pts1 = np.float32([tl, bl, tr, br])
    pts2 = np.float32([[0, 0], [0, 1080], [1920, 0], [1920, 1080]])

    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    # print("Bird-eye-view Matrix: \n", matrix)
    t_frame = cv2.warpPerspective(frame, matrix, (1920, 1080))

    return t_frame


if __name__ == "__main__":
    # test image
    # image = cv2.imread('./test_images/24_19-48-02.png')

    # video capture from the camera
    ch0 = cv2.VideoCapture(0)
    ch0.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    ch0.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    while True:
        # read frame
        _, frame = ch0.read()

        # transform the frame into bird eye view
        transformed_frame = bev(frame)
        # show the images
        cv2.imshow("Frame", frame)
        cv2.imshow("Transformed_frame Bird Eye View", transformed_frame)

        if cv2.waitKey(1) == 27:
            break