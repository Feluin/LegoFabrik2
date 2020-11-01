import ctypes
from typing import Any, List, Union

import numpy as np

class Sonar(object):
    LEFT = 6
    LEFT45 = 3
    LEFT_FRONT = 4
    RIGHT_FRONT = 5
    RIGHT45 = 0
    RIGHT = 1
    BACK = None

    def __init__(self):
        # FIXME: How many sonic devices have you plugged in? default: 7
        self._sensor_count = 4

        self._sonic = ctypes.CDLL('/usr/local/lib/libsonic.so')
        self._sonic.measure.restype = ctypes.c_double
        self._sonic.initialize()

    def _try_read(self, sensor, times=3):
        for _ in range(times):
            ret = self.read(sensor)
            if ret != None:
                return ret
        return None

    def read(self, sensor: int):
        """
        Read try to read a sensor value
        :param sensor: the id of the sensor.
        :return: the read distance (rounded) or `None` if read failed
        """
        ret = self._sonic.measure(ctypes.c_uint(sensor))
        return np.nan if ret == 0 else round(ret, 2)

    def read_all(self):
        """
        Read all sensors.
        :return: an array having `self._sensor_count` items. if error occurred on
        sensor, the item is `None`.
        """
        results = []
        for i in range(self._sensor_count):
            ret = self.read(i)
            if ret == None:
                ret = self._try_read(i)
            results.append(ret)
        return results
