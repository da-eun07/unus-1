import Arduino.ar_util_func as ar_util
import Vision.cam_util_func as cam_util
import Vision.lane_detection as lane_util
import Vision.traffic_light_detection as tf_util
import cv2
from socket import *
from struct import iter_unpack
import numpy as np
from datetime import datetime

# MISSION : OBSTACLE + TRAFFIC LIGHT

#################### Check before Test ####################
# ARDUINO CONNECTION
ser = ar_util.libARDUINO()
comm = ser.init('/dev/tty.usbmodem101', 9600) #COM7
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
ar_count = 1
steer_hist = ['right'] # history list of lane result
new_sig_count = 1
new_obs_sig_count = 0
obs = 'f' # the place of the obstacle

# send command to the arduino with speed ~ means delay in this function
def send_command(command, speed):
    # speed min: 15
    global ar_count # use the global variable counting while reading the camera
    if ar_count >= speed:  ### FIX ME
        print('To Arduino: ' + command)
        comm.write(command.encode())
        # print the timestamp
        print(datetime.now().timestamp())
        # reset the counting
        ar_count = 0
# mapping steering result and the command required in arduino code (check package Arduino)
# and send them to arduino
def steer_signal(steer):
    if steer == 'forward':
        send_command("4", speed=1)
    elif steer == 'leftleftleft':
        send_command("1", speed=1)
    elif steer == 'leftleft':
        send_command("2", speed=1)
    elif steer == 'left':
        send_command("3", speed=1)
    elif steer == 'right':
        send_command("5", speed=1)
    elif steer == 'rightright':
        send_command("6", speed=1)
    elif steer == 'rightrightright':
        send_command("7", speed=1)
    elif steer == 'obstacle':
        send_command(obs, speed=1)  # obs is one of 'c', 'm', 'f'
    elif steer == 'stop':  # stop
        send_command("9", speed=1)
    else: # traffic - not used
        send_command("r", speed=1)

# just enter or insert 'c', 'm', 'f'
obs = input("Enter to start")

if obs == 'c' or obs == 'm' or obs == 'f':
    steer_signal('forward')
else:
    obs = 'f'
    steer_signal('forward')

# MAIN LOOP : LANE + OBSTACLE
while True:
    # counting by every frame
    ar_count += 1
    # camera on
    _, frame0, _, frame1 = cam.camera_read(ch0, ch1)
    # show the camera images
    cam.image_show(frame0, frame1)

    # get lane info from frame0
    # _, hough = LD.hough_lane(frame0)
    # cv2.imshow('hough image', hough)
    # get the steering
    steer, lane_image = LD.side_lane(frame0, 'slow')
    cv2.imshow('lane image', lane_image)

    if new_sig_count == 0:
        # print('0')
        # compare with the history list and if it is different with the last one, make new_sig_count to 1
        if steer_hist[-1] != steer:
            new_sig_count = 1
    elif new_sig_count == 1 or new_sig_count == 2:
        # print('1')
        # if the new signal came after then count up the new_sig_count
        if steer_hist[-1] == steer:
            new_sig_count += 1
        # if not reset it
        else:
            new_sig_count = 0
    elif new_sig_count >= 3: # '3' is a kind of buffer
        # print('2')
        # send the steer signal
        steer_signal(steer)
        # reset the new_sig_count
        new_sig_count = 0
    # append new steering info to the history list
    steer_hist.append(steer)

    # LIDAR COMMUNICATION
    # GET OBSTACLE INFO
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
            new_obs_sig_count += 1
        elif y[0] == 65533:  # 3-2) criteria - none
            # print("{}th Criteria : Nothing".format(li_count))
            dis_detected = 0
            new_obs_sig_count = 0
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

    # if more than 3 signals in the range of obstacle
    if new_obs_sig_count == 3:  ### FIX ME
        # send the signal to avoid the obstacle and break
        steer_signal("obstacle")
        break

    if cam.loop_break():
        steer_signal("stop")
        ser.close()
        break
    if cam.capture(frame0):
        continue

### 본 통신 끝 ####
data = connectionSock.recv(1024)
# print(data.decode("utf-8"))
print("Lidar communication finished")

# OBSTACLE AVOIDING
while True:
    if comm.readable():  # read the serial
        if comm.readline().decode("utf-8").rstrip() == 'of': # if the avoiding finished
            # print and break
            print("Finished obstacle")
            break

# reset the variables for driving
ar_count = 1
steer_hist = ['right']
new_sig_count = 1
new_tf_sig_count = 0

# MAIN LOOP : LANE AGAIN + TRAFFIC LIGHT RED
# there's no explanation of repeated part
while True:
    ar_count += 1
    _, frame0, _, frame1 = cam.camera_read(ch0, ch1)
    cam.image_show(frame0, frame1)

    # _, hough = LD.hough_lane(frame0)
    # cv2.imshow('hough image', hough)
    steer, lane_image = LD.side_lane(frame0)
    cv2.imshow('lane image', lane_image)

    # get the traffic light info from frame1
    traffic = TF.color_detection(frame1)
    # if the 'stop' signal came after 5 times send signal to the arduino
    if traffic == 'stop':
        new_tf_sig_count += 1
    if new_tf_sig_count == 5:
        steer_signal('stop')
        break

    if new_sig_count == 0:
        # print('0')
        if steer_hist[-1] != steer:
            new_sig_count = 1
    elif new_sig_count == 1 or new_sig_count == 2:
        # print('1')
        if steer_hist[-1] == steer:
            new_sig_count += 1
        else:
            new_sig_count = 0
    elif new_sig_count >= 3:
        # print('2')
        steer_signal(steer)
        new_sig_count = 0
    #print(steer)
    steer_hist.append(steer)

    if cam.loop_break():
        steer_signal("stop")
        ser.close()
        break
    if cam.capture(frame1):
        continue

ar_count = 1
steer_hist = ['right']
new_sig_count = 1
new_tf_sig_count = 0

# MAIN LOOP : LANE AGAIN + TRAFFIC LIGHT GREEN
while True:
    ar_count += 1
    _, frame0, _, frame1 = cam.camera_read(ch0, ch1)
    cam.image_show(frame0, frame1)

    # _, hough = LD.hough_lane(frame0)
    # cv2.imshow('hough image', hough)
    steer, lane_image = LD.side_lane(frame0)
    cv2.imshow('lane image', lane_image)

    # get the traffic light info from frame1
    traffic = TF.color_detection(frame1)
    # print(traffic)
    # if the 'go' signal came after more than 5 times send 'forward' signal to the arduino and break
    if traffic == 'go':
        new_tf_sig_count += 1
        print(new_tf_sig_count)
    if new_tf_sig_count >= 5:
        steer_signal('forward')
        break

    if cam.loop_break():
        steer_signal("stop")
        ser.close()
        break
    if cam.capture(frame0):
        continue

# LOOP FOR DRIVING
while True:
    ar_count += 1
    _, frame0, _, frame1 = cam.camera_read(ch0, ch1)
    cam.image_show(frame0, frame1)

    _, hough = LD.hough_lane(frame0)
    cv2.imshow('hough image', hough)
    steer, lane_image = LD.side_lane(frame0)
    cv2.imshow('lane image', lane_image)

    if new_sig_count == 0:
        # print('0')
        if steer_hist[-1] != steer:
            new_sig_count = 1
    elif new_sig_count == 1:
        # print('1')
        if steer_hist[-1] == steer:
            new_sig_count += 1
        else:
            new_sig_count = 0
    elif new_sig_count >= 2:
        # print('2')
        steer_signal(steer)
        new_sig_count = 0
    # print(steer)
    steer_hist.append(steer)

    if cam.loop_break():
        steer_signal("stop")
        ser.close()
        break
    if cam.capture(frame0):
        continue
