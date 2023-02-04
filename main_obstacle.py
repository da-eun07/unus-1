import Arduino.ar_util_func as ar_util
import Vision.cam_util_func as cam_util
import Vision.lane_detection as lane_util
import Vision.traffic_light_detection as tf_util
import cv2
from socket import *
from struct import iter_unpack
import numpy as np

# MISSION_1 : AVOID OBSTACLE

#################### Check before Test ####################
# ARDUINO CONNECTION
ser = ar_util.libARDUINO()
comm = ser.init('/dev/tty.usbmodem114101', 9600) #COM7
# CAMERA CONNECTION
cam = cam_util.libCAMERA()
ch0, ch1 = cam.initial_setting_480(cam0port=0, cam1port=1, capnum=2) # if window cam.initial_setting
print("new terminal-python Lidar/lidar_shoot.py")
#################### Check before Test ####################
# LIDAR CONNECTION
#### initialize #####
serverSock = socket(AF_INET, SOCK_STREAM)
serverSock.bind(('127.0.0.1',8080)) # 본인 무선 LAN IPv4도 가능
serverSock.listen(1)
connectionSock, addr = serverSock.accept()
print("접속 IP: {}".format(str(addr)))
## 클라이언트로부터 메세지 한번 받기 ##
data = connectionSock.recv(1024)
print("IP{}의 message: {}".format(str(addr), data))

uvR=np.array([])
dis_detected=0
buffer=np.array([])  # 버퍼 역할
# 수신 반복 횟수 측정
li_count = 0

# LANE DETECTION
LD = lane_util.libLANE()
# TRAFFIC LIGHT DETECTION
TF = tf_util.libTRAFFIC()
# VARIABLES
global ar_count
ar_count = 0
ob_count = 0
steer_hist = []
new_sig_count = 0

def send_command(command, speed):
    # speed min: 15
    global ar_count
    if ar_count == speed:  ### FIX ME
        print('To Arduino: ' + command)
        comm.write(command.encode())
        ar_count = 0

# MAIN LOOP
while True:
    ar_count += 1
    # CAMERA ON
    _, frame0, _, frame1 = cam.camera_read(ch0, ch1)
    cam.image_show(frame0, frame1)

    # GET LANE INFO USING frame0
    # _, hough = LD.hough_lane(frame0)
    # cv2.imshow('hough image', hough)
    steer, lane_image = LD.side_lane(frame0)
    steer_hist.append(steer)
    cv2.imshow('lane image', lane_image)

    if (MODE == "DRIVE"):
        # print('Lets Drive')
        if new_sig_count == 0:
            if steer_hist[-1] != steer:
                new_sig_count += 1
        elif new_sig_count == 1 or new_sig_count == 2:
            if steer_hist[-1] == steer:
                new_sig_count += 1
            else:
                new_sig_count = 0
        elif new_sig_count == 3:
            new_sig_count = 0
            if steer == 'forward':
                send_command("0", speed=1)
            elif steer == 'right':
                send_command("1", speed=1)
            elif steer == 'left':
                send_command("-1", speed=1)
            else:  # stop
                send_command("10", speed=1)

    elif (MODE == "MISSION_1"):
        # print('Lets Avoid Obstacle')
        # LIDAR COMMUNICATION
        # 데이터 수신
        data = connectionSock.recv(3000)  # Fix me
        # 데이터 확인
        for y in iter_unpack('HHH', data):  # get u, v, r
            if y[0] == 65531:  # 1) start
                li_count += 1
                j = 0
            elif y[0] == 65532:  # 3-1) criteria - Detected
                print("{}th Criteria : Detected".format(li_count))
                dis_detected = round(y[2] * 0.4)
            elif y[0] == 65533:  # 3-2) criteria - none
                print("{}th Criteria : Nothing".format(li_count))
                dis_detected = 0
            elif y[0] == 65534:  # 4) finish
                uvR = buffer
                buffer = np.array([])
                print("mean value / u = {}, v = {}, R = {}".format(np.nanmean(uvR[:][0]), np.nanmean(uvR[:][1]),
                                                                   np.nanmean(uvR[:][2])))
                print("통신, 데이터 개수 {}개!".format(li_count, uvR.size // 2))
                print(li_count)
            else:  # 2) u, v, R data
                u_converted = round(y[0] * 0.01)
                v_converted = round(y[1] * 0.0075)
                R_converted = round(y[2] * 0.4)
                buffer = np.append(buffer, np.array([u_converted, v_converted, R_converted]))

        # GET OBSTACLE INFO
        OBSTACLE = None
        if OBSTACLE:
            ob_count += 1
            if OBSTACLE == 'First Detect':  # Left Obstacle
                print("Avoiding First Obstacle")
                send_command("-2", speed=30)  ### FIX ME
            elif OBSTACLE == 'Second Detect':  # Right Obstacle
                print("Avoiding Second Obstacle")
                send_command("2", speed=30)  ### FIX ME
        else:  # If no obstacles
            if steer == 'forward':
                send_command("0", speed=15)
            elif steer == 'right':
                send_command("1", speed=15)
            elif steer == 'left':
                send_command("-1", speed=15)
            else:  # stop
                send_command("10", speed=15)
        if ob_count == 2:  # No more obstacles
            print("Avoided all Obstacles")
    elif (MODE == "MISSION_2"):
        print("traffic light")
    elif (MODE == "MISSION_3"):
        print("mission2: parking")

    if cam.loop_break():
        ser.close()
        break
    if cam.capture(frame0):
        continue

### 본 통신 끝 ####
data = connectionSock.recv(1024)
print(data.decode("utf-8"))
print("Complete sending message")