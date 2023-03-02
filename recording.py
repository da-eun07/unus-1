# CAMERA RECORDING
import datetime
import cv2

# load the first camera
cam0port = 0
ch0 = cv2.VideoCapture(cam0port)

# find out whether the camera is open or not
if ch0.isOpened():
    print("Camera Channel0 is enabled!")

# define the codec
fourcc = cv2.VideoWriter_fourcc(*'DIVX')
record = False

while True:
    # read camera frame
    _, frame0 = ch0.read()
    cv2.imshow("VideoFrame", frame0)

    # make a string for the current time
    now = datetime.datetime.now().strftime("%d_%H-%M-%S")
    # wait for the key
    key = cv2.waitKey(1)

    if key == ord('q') or key == ord('Q'): # end the camera reading
        break
    elif key == ord('c') or key == ord('C'): # capture the image of the time
        print("캡쳐")
        cv2.imwrite("./record/" + str(now) + ".jpg", frame0)
    elif key == ord('r') or key == ord('R'): # start recording
        print("녹화 시작")
        record = True
        # write video with the given codec and the size
        video = cv2.VideoWriter("./record/" + str(now) + ".avi", fourcc, 20.0, (frame0.shape[1], frame0.shape[0]))
    elif key == ord('s') or key == ord('S'): # end recording
        print("녹화 중지")
        record = False
        video.release()

    if record == True: # print while recording
        print("녹화 중..")
        video.write(frame0)

# destroy the window
cv2.destroyAllWindows()