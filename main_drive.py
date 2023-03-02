import Arduino.ar_util_func as ar_util
import Vision.cam_util_func as cam_util
import Vision.lane_detection as lane_util
import cv2
from datetime import datetime

# DRIVE

#################### Check before Test ####################
# ARDUINO CONNECTION
ser = ar_util.libARDUINO()
comm = ser.init('/dev/tty.usbmodem101', 9600) #COM7
# CAMERA CONNECTION
cam = cam_util.libCAMERA()
ch0, ch1 = cam.initial_setting_480(cam0port=0, cam1port=1, capnum=2) # if window cam.initial_setting
#################### Check before Test ####################

# LANE DETECTION
LD = lane_util.libLANE()
# VARIABLES
global ar_count
ar_count = 1
steer_hist = ['right'] # history list of lane result
new_sig_count = 1

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
        send_command("8", speed=1)
    elif steer == 'stop':  # stop
        send_command("9", speed=1)
    else: # traffic
        send_command("r", speed=1)

input("Enter to start")
# gives the first signal to go forward
steer_signal('forward')

# MAIN LOOP
while True:
    # counting by every frame
    ar_count += 1
    # camera on
    _, frame0, _, frame1 = cam.camera_read(ch0, ch1)
    # show the camera images
    cam.image_show(frame0, frame1)

    # get lane info from frame0
    _, hough = LD.hough_lane(frame0)
    cv2.imshow('hough image', hough)
    # get the steering
    steer, lane_image = LD.side_lane(frame0)
    cv2.imshow('lane image', lane_image)

    if new_sig_count == 0:
        # print('0')
        # compare with the history list and if it is different with the last one, make new_sig_count to 1
        if steer_hist[-1] != steer:
            new_sig_count = 1
    elif new_sig_count == 1:
        # print('1')
        # if the new signal came after then count up the new_sig_count
        if steer_hist[-1] == steer:
            new_sig_count += 1
        # if not reset it
        else:
            new_sig_count = 0
    elif new_sig_count >= 2: # '2' is a kind of buffer
        # print('2')
        # send the steer signal
        steer_signal(steer)
        # reset the new_sig_count
        new_sig_count = 0
    # append new steering info to the history list
    steer_hist.append(steer)

    # if 'q' end camera reading and stop the car
    if cam.loop_break():
        steer_signal("stop")
        # close serial port
        ser.close()
        break
    # if 'c' capture the frame0
    if cam.capture(frame0):
        continue
