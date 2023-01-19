import datetime
import cv2
import Vision.cam_util_func as cam_util

cam = cam_util.libCAMERA()
ch0, ch1 = cam.initial_setting(cam0port=0, cam1port=1, capnum=2)

fourcc = cv2.VideoWriter_fourcc(*'MP4V')
record = False

while True:

    _, frame0, _, frame1 = cam.camera_read(ch0, ch1)
    cv2.imshow("VideoFrame", frame1)

    now = datetime.datetime.now().strftime("%d_%H-%M-%S")
    key = cv2.waitKey(30)

    if key == 27:
        break
    elif key == 26:
        print("캡쳐")
        cv2.imwrite("./record/" + str(now) + ".png", frame1)
    elif key == 24:
        print("녹화 시작")
        record = True
        video = cv2.VideoWriter("./record/" + str(now) + ".mp4", fourcc, 20.0, (frame1.shape[1], frame1.shape[0]))
    elif key == 3:
        print("녹화 중지")
        record = False
        video.release()

    if record == True:
        print("녹화 중..")
        video.write(frame1)

cv2.destroyAllWindows()