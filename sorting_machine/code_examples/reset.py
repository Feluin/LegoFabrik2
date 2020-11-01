
from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division       #                           ''

import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.

BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.TOUCH)

try:
    BP.set_motor_dps(BP.PORT_A, 80)
    time.sleep(3)
    BP.set_motor_dps(BP.PORT_A, 80)

    value = BP.get_sensor(BP.PORT_1)

    while value != 1:
        
        try:
            value = BP.get_sensor(BP.PORT_1)
            print(value)
        except brickpi3.SensorError as error:
            print(error)
        
    BP.set_motor_dps(BP.PORT_A, 50)
    time.sleep(0.4)
    BP.set_motor_dps(BP.PORT_A, 0)
except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
    BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
