import Arduino.ar_util_func as ar_util
import Vision.cam_util_func as cam_util

mode_list = ["DRIVE", "MISSION_1", "MISSION_2"]

select_mode = int(input("Select mode (0:Drive, 1:Mission_1, 2: Mission_2): "))

if select_mode == 0 or select_mode == 1 or select_mode == 2:
    MODE = mode_list[select_mode]
    print("MODE: " + MODE)
else:
    print("Invalid Input")
    exit()

# ARDUINO CONNECTION
ser = ar_util.libARDUINO()  ### FIX ME
comm = ser.init('/dev/tty.usbmodem14301', 9600)

# CAMERA CONNECTION
cam = cam_util.libCAMERA()
ch0, ch1 = cam.initial_setting_480(cam0port=0, cam1port=1, capnum=2)

input_value = 0
count = 0

# New variable to track the number of times cv_output has been received
cv_output_count = 0

# MAIN LOOP
while True:

    count += 1
    # 실시간 loop
    if count == 20:
        input_value = 255
        input_value_str = str(input_value)
        comm.write(input_value_str.encode())
    elif count == 40:
        input_value = 0
        count = 0
        input_value_str = str(input_value)
        comm.write(input_value_str.encode())

    _, frame0, _, frame1 = cam.camera_read(ch0, ch1)
    cam.image_show(frame0, frame1)

    if cam.loop_break():
        ser.close()
        break
