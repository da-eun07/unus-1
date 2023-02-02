import datetime
import cv2
import Vision.cam_util_func as cam_util

cam0port = 0
ch0 = cv2.VideoCapture(cam0port)

if ch0.isOpened():
    print("Camera Channel0 is enabled!")

fourcc = cv2.VideoWriter_fourcc(*'DIVX')
record = False

while True:

    _, frame0 = ch0.read()
    cv2.imshow("VideoFrame", frame0)

    now = datetime.datetime.now().strftime("%d_%H-%M-%S")
    key = cv2.waitKey(1)

    if key == ord('q') or key == ord('Q'):
        break
    elif key == ord('c') or key == ord('C'):
        print("캡쳐")
        cv2.imwrite("./record/" + str(now) + ".jpg", frame0)
    elif key == ord('r') or key == ord('R'):
        print("녹화 시작")
        record = True
        video = cv2.VideoWriter("./record/" + str(now) + ".avi", fourcc, 20.0, (frame0.shape[1], frame0.shape[0]))
    elif key == ord('s') or key == ord('S'):
        print("녹화 중지")
        record = False
        video.release()

    if record == True:
        print("녹화 중..")
        video.write(frame0)

cv2.destroyAllWindows()