import Arduino.ar_util_func as ar_util
import Vision.cv_util_func as cv_util
import Vision.cam_util_func as cam_util

mode_list = ["DRIVE", "MISSION_1", "MISSION_2"]
# EPOCH = 500000
arduino_port = 'COM7' ### FIX ME

if __name__ == "__main__":
    # MODE SELECTING
    while True:
        select_mode = int(input("Select mode (0:Drive, 1:Mission_1, 2: Mission_2): "))
        if select_mode == 0 or select_mode == 1 or select_mode == 2:
            break
        else:
            print("Invalid Input")

    MODE = mode_list[select_mode]
    print("MODE: " + MODE)

    # ARDUINO CONNECTING
    ser = ar_util.libARDUINO()
    comm = ser.init(arduino_port, 9600)
    # CAMERA CONNECTING
    cam = cam_util.libCAMERA()
    ch0, ch1 = cam.initial_setting(cam0port=0, cam1port=1, capnum=2)

    while True:
        input_value = 0
        comm.write(input_value.encode()) # direction input

        _, frame0, _, frame1 = cam.camera_read(ch0, ch1)
        cam.image_show(frame0, frame1)

        # DRIVE MODE
        if (MODE == "DRIVE"):
            print("let's go")


        # MISSION_1 MODE: OPSTACLE + TRAFFIC LIGHT
        elif (MODE == "MISSION_1"):
            print("mission1: opstacle + traffic light")
            # while 2개로 하나씩 치우기



        # MISSION_2 MODE: PARKING
        elif (MODE == "MISSION_2"):
            print("mission2: parking")


        if cam.loop_break():
            break

