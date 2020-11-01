import time     
import brickpi3 
import csv 
import sys

BP = brickpi3.BrickPi3() 
BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.TOUCH)

class Pusher:

    dps = None
    seconds = None
    pushCounter = 0

    def rotate(self,signature):                         # Method for moving rotating the push mechanism depending on the object in the pallet
        direction = self.identifyDirection(signature)   # Reading the rotation direction of the pusher for the detected object signature
        
        if direction == 'left':                         # Setting speed and length of the rotation.
            dps = -360
            seconds = 2.5
        elif direction == 'right':
            dps = 360
            seconds = 2.5
        try:
            BP.set_motor_dps(BP.PORT_A, dps)            # Performing the rotation
            time.sleep(seconds)
            BP.set_motor_dps(BP.PORT_A, 0)  
            
            BP.set_motor_dps(BP.PORT_A, -dps)           # Resetting the pusher to its initial position
            time.sleep(seconds)
            BP.set_motor_dps(BP.PORT_A, 0)
            
            self.pushCounter = self.pushCounter + 1     # increasing the counts of pushes
            if self.pushCounter % 15 == 0:              # calibrating the pusher if 15 pushes have been performed.
                self.calibrate()
                
        except KeyboardInterrupt:                       # except the program gets interrupted by Ctrl+C on the keyboard.
            BP.reset_all()                              # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.

    def calibrate(self):                                # Method used for calibration of the pusher position, runned on initialization of the machine

        BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.TOUCH) 
        print('calibrating the pusher...')
        try:
            BP.set_motor_dps(BP.PORT_A, 80)  
            time.sleep(3)
            BP.set_motor_dps(BP.PORT_A, 80)             # Start rotating until the touch sensor is triggered

            value = BP.get_sensor(BP.PORT_1)

            while value != 1:
                
                try:
                    value = BP.get_sensor(BP.PORT_1)
                    
                except brickpi3.SensorError as error:
                    print(error)
                
            BP.set_motor_dps(BP.PORT_A, 50)             # When the sensor is triggered, move a little to compensate for small inaccuracies
            time.sleep(0.4)
            BP.set_motor_dps(BP.PORT_A, 0)              # The pusher is calibrated and stops moving
            print('pusher calibrated')
        except KeyboardInterrupt:                       # except the program gets interrupted by Ctrl+C on the keyboard.
            BP.reset_all()                              # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
            
    def identifyDirection(self,signature):              
        with open('positions.csv') as csvfile:
                readCSV = csv.reader(csvfile, delimiter=',' )
                for row in readCSV:
                    if row[0] == str(signature):
                        direction = row [3]
                        return direction

    def release(self):                                  # Method for releasing the pressure of the touch sensor, when the machine is being shut down. 
                                                        # The pressure is released by rotating the pusher so that the touch sensor is not pressed
        BP.set_motor_dps(BP.PORT_A, 80)
        time.sleep(1)
        BP.set_motor_dps(BP.PORT_A, 0)