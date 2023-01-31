import Arduino.ar_util_func as ar_util
import Vision.cam_util_func as cam_util
import Vision.lane_detection as lane_util
import Vision.traffic_light_detection as tf_util
import cv2

# DRIVE
# MISSION_1 : AVOID OBSTACLE
# MISSION_2 : TRAFFIC LIGHT
# MISSION_3 : PARKING
mode_list = ["DRIVE", "MISSION_1", "MISSION_2", "MISSION_3"]
select_mode = int(input("Select mode (0:Drive, 1:Mission_1, 2: Mission_2, 3: Mission_3): "))
if select_mode == 0 or select_mode == 1 or select_mode == 2 or select_mode == 3:
    MODE = mode_list[select_mode]
    print("MODE: " + MODE)
else:
    print("Invalid Input")
    exit()

# ARDUINO CONNECTION
ser = ar_util.libARDUINO()  ### FIX ME
comm = ser.init('COM7', 9600)
# CAMERA CONNECTION
cam = cam_util.libCAMERA()
ch0, ch1 = cam.initial_setting(cam0port=0, cam1port=1, capnum=2)
# LIDAR CONNECTION
Li_PortNum = "/dev/tty.usbserial-11410"  ### FIX ME

# LANE DETECTION
LD = lane_util.libLANE()
# VARIABLES
global AR_COUNT
AR_COUNT = 0
OB_COUNT = 0
TRAFFIC_COUNT = 0 # <-> Distance

def send_command(command, speed):
    global AR_COUNT
    if AR_COUNT == speed:  ### FIX ME
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
    cv2.imshow('lane image', lane_image)

    if (MODE == "DRIVE"):
        # print('Lets Drive')
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
        # GET OBSTACLE INFO
        LI = lidar_util.libLIDAR()
        OBSTACLE = lidar_util.get_signal()
        if OBSTACLE:
            OB_COUNT += 1
            if OBSTACLE == 'First Detect':  # Left Obstacle
                print("Avoiding First Obstacle")
                send_command("-2", speed=30)  ### FIX ME
            elif OBSTACLE == 'Second Detect':  # Right Obstacle
                print("Avoiding Second Obstacle")
                send_command("2", speed=30)  ### FIX ME
        else:  # If no obstacles
            if steer == 'forward':
                send_command("0", speed=1)
            elif steer == 'right':
                send_command("1", speed=1)
            elif steer == 'left':
                send_command("-1", speed=1)
            else:  # stop
                send_command("10", speed=1)
        if OB_COUNT == 2:  # No more obstacles
            print("Avoided all Obstacles")
    elif (MODE == "MISSION_2"):
        # print('traffic light')
        # GET TRAFFIC LIGHT INFO USING frame1
        TRAFFIC_COUNT += 1
        TF = tf_util.libTRAFFIC()
        if TRAFFIC_COUNT > 100:
            TRAFFIC = TF.traffic_detection(frame1, sample=16, print_enable=True)
        else:
            TRAFFIC = 'NOT_YET'

        if TRAFFIC == 'GREEN' or TRAFFIC == 'NOT_YET': ### FIX ME : HOW FAR?
            if steer == 'forward':
                send_command("0", speed=1)
            elif steer == 'right':
                send_command("1", speed=1)
            elif steer == 'left':
                send_command("-1", speed=1)
        elif TRAFFIC == 'RED' or TRAFFIC == 'YELLOW':  # stop
            send_command("10", speed=1)
    elif (MODE == "MISSION_3"):
        # print("mission2: parking")
        send_command("100")

    if cam.loop_break():
        ser.close()
        break
    if cam.capture(frame0):
        continue
