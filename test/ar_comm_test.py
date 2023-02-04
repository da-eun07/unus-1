import serial
import time

ArduinoSerial = serial.Serial('/dev/tty.usbmodem101', 9600, timeout=1)
time.sleep(2)
count = 0
while True:
    count += 1
    # print("enter number")
    # var = input()
    if count % 2 == 0:
        var = 1
    else:
        var = -1
    print("you entered", var)
    var_str = str(var)
    ArduinoSerial.write(var_str.encode())
    data = ArduinoSerial.readline()[:-2]
    print(data)
    # var += 1