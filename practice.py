# ARDUINO EXERCISE

import Arduino.ar_util_func as ar_util

arduino_port = '/dev/cu.usbmodem1101' ### FIX ME

ser = ar_util.libARDUINO()
comm = ser.init(arduino_port, 9600)

while True:
    input_value = input('아두이노로 전송할 저항 값(0~255): ')

    comm.write(input_value.encode())

    if input_value == 'q':
        break