import sys
import time
import serial                        # pip install serial
import numpy as np                   # pip install numpy

np.set_printoptions(threshold=sys.maxsize, linewidth=150)
WAIT_TIME = 2

class libARDUINO(object):
    def __init__(self):
        self.port = None
        self.baudrate = None
        self.wait_time = WAIT_TIME  # second unit

    # Arduino Serial USB Port Setting
    def init(self, port, baudrate):
        ser = serial.Serial()
        ser.port, self.port = port, port
        ser.baudrate, self.baudrate = baudrate, baudrate
        ser.open()
        time.sleep(self.wait_time)
        return ser