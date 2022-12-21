#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lsusb to check device name
# dmesg | grep "tty" to find port name

import serial
import time


if __name__ == '__main__':
    print('Running. Press CTRL-C to exit.')
    with serial.Serial("/dev/ttyACM0", 115200, timeout=0.01) as arduino:
        time.sleep(0.1)  # wait for serial to open
        print("after sleep")
        if arduino.isOpen():
            print("{} connected!".format(arduino.port))
            try:
                f = 1
                while True:
                    f = f + 1
                    arduino.write(f'<{f}>'.encode())

                    while arduino.inWaiting() == 0:
                        pass
                    # if arduino.inWaiting() > 0:
                    #     answer = arduino.readlines()
                    #     for line in answer:
                    #         print(f'Response {line}')
                    #     arduino.flushInput()  # remove data after reading
                    time.sleep(0.200)
                    if f == 9:
                        f = 1
            except KeyboardInterrupt:
                print("KeyboardInterrupt has been caught.")
