import ctypes
import pigpio
from typing import Any, List, Union

class Sonic (object):
    def __init__(self):
        self.sonic = ctypes.CDLL("/usr/local/lib/libsonic.so")
        self.sonic.measure.restype = ctypes.c_double
        self.sonic.initialize()

    def getDistance(self):
        results = []
        # FIXME: How many sonic devices have you plugged in? default: 7
        for i in range(7):
            returnValue = self.sonic.measure(ctypes.c_uint(i))
            if returnValue == 0:
                i -= 1
            else:
                results.append(round(returnValue, 2))
        return results


sonic = Sonic()
try:
    while True:
        distance = sonic.getDistance()
        print(distance)
        # if distance == []:
        #    print('No distances measured.')
        # else:
        #    print("left: ", distance[0], " left45: ", distance[1], " left_front: ", distance[2], " right_front: ",
        #          distance[3], " right45: ", distance[4], " right: ", distance[5], " back: ", distance[6])

except KeyboardInterrupt:
    print("ende")
