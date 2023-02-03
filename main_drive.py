import Arduino.ar_util_func as ar_util
import Vision.cam_util_func as cam_util
import Vision.lane_detection as lane_util
import cv2

# DRIVE

#################### Check before Test ####################
# ARDUINO CONNECTION
ser = ar_util.libARDUINO()
comm = ser.init('/dev/tty.usbmodem114101', 9600) #COM7
# CAMERA CONNECTION
cam = cam_util.libCAMERA()
ch0, ch1 = cam.initial_setting_480(cam0port=0, cam1port=1, capnum=2) # if window cam.initial_setting
print("new terminal-python Lidar/lidar_shoot.py")
#################### Check before Test ####################

# LANE DETECTION
LD = lane_util.libLANE()
# VARIABLES
global AR_COUNT
AR_COUNT = 0
steer_hist = []
NEW_SIG_COUNT = 0

def send_command(command, speed):
    # speed min: 15
    global AR_COUNT
    if AR_COUNT == speed:  ### FIX ME
        print('To Arduino: ' + command)
        comm.write(command.encode())
        AR_COUNT = 0

# MAIN LOOP
while True:
    AR_COUNT += 1
    # CAMERA ON
    _, frame0, _, frame1 = cam.camera_read(ch0, ch1)
    cam.image_show(frame0, frame1)

    # GET LANE INFO USING frame0
    # _, hough = LD.hough_lane(frame0)
    # cv2.imshow('hough image', hough)
    steer, lane_image = LD.side_lane(frame0)
    steer_hist.append(steer)
    cv2.imshow('lane image', lane_image)

    if NEW_SIG_COUNT == 0:
        if steer_hist[-1] != steer:
            NEW_SIG_COUNT += 1
    elif NEW_SIG_COUNT == 1 or NEW_SIG_COUNT == 2:
        if steer_hist[-1] == steer:
            NEW_SIG_COUNT += 1
        else:
            NEW_SIG_COUNT = 0
    elif NEW_SIG_COUNT == 3:
        NEW_SIG_COUNT = 0
        if steer == 'forward':
            send_command("0", speed=1)
        elif steer == 'right':
            send_command("1", speed=1)
        elif steer == 'left':
            send_command("-1", speed=1)
        else:  # stop
            send_command("10", speed=1)

    if cam.loop_break():
        ser.close()
        break
    if cam.capture(frame0):
        continue
