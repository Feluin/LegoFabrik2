#!/usr/bin/env python
import brickpi3 # import the BrickPi3 drivers
import time
BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.


BP.set_motor_dps(BP.PORT_B, 0)


