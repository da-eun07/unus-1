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
steer_hist = ['right']
new_sig_count = 1

def send_command(command, speed):
    # speed min: 15
    global ar_count
    if ar_count >= speed:  ### FIX ME
        print('To Arduino: ' + command)
        comm.write(command.encode())
        print(datetime.now().timestamp())
        ar_count = 0
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
    else:  # stop
        send_command("9", speed=1)

input("Enter")
steer_signal('forward')

# MAIN LOOP
while True:
    ar_count += 1
    # CAMERA ON
    _, frame0, _, frame1 = cam.camera_read(ch0, ch1)
    cam.image_show(frame0, frame1)

    # GET LANE INFO USING frame0
    _, hough = LD.hough_lane(frame0)
    cv2.imshow('hough image', hough)
    steer, lane_image = LD.side_lane(frame0)
    cv2.imshow('lane image', lane_image)

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
    if cam.capture(frame0):
        continue
