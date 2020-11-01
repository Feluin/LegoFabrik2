import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers
import csv      

BP = brickpi3.BrickPi3()                                    # Create an instance of the BrickPi3 class.
BP.set_sensor_type(BP.PORT_2, BP.SENSOR_TYPE.TOUCH)

class Band:
    sortCounter = 0
    def moveTo(self,signature):                              # Method for moving the band to one of the seven preset positions
        dps = None
        seconds = None
        with open('positions.csv') as csvfile:              # Reading the csv file, containing instructions how to reach the preset position
            readCSV = csv.reader(csvfile, delimiter=',' )
            for row in readCSV:
                if row[0] == str(signature):
                    dps = float(row[1])                     # Row 1 of the CSV indicates the rotation speed in degrees per second
                    seconds = float(row[2])                 # Row 2 of the CSV indicates how long the movement should proceed with that speed.
        try:
            BP.set_motor_dps(BP.PORT_B, dps)                # Moving the band to the preset position
            time.sleep(seconds)
            BP.set_motor_dps(BP.PORT_B, 0)

            self.sortCounter = self.sortCounter + 1
            if self.sortCounter % 15 == 0:                      # calibrating the band if 5 sorting cycles have been performed.
                    self.calibrate()
        except KeyboardInterrupt:                           # except the program gets interrupted by Ctrl+C on the keyboard.
            BP.reset_all()                                  # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.


    def reset(self,signature):                               # Method for returning the band to the initial position after sorting.
        dps = None
        seconds = None
        with open('positions.csv') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',' )
            for row in readCSV:
                if row[0] == str(signature):
                    dps = float(row[1])                     # Row 1 of the CSV indicates the rotation speed in degrees per second
                    seconds = float(row[2])                 # Row 2 of the CSV indicates how long the movement should proceed with that speed.
        try:
            BP.set_motor_dps(BP.PORT_B, -dps)               # Travel time to initial position will take route to the corresponding position + route to camera module(7.5s)
            time.sleep(seconds + 7.5)
            BP.set_motor_dps(BP.PORT_B, 0)       
    
        except KeyboardInterrupt:                           # except the program gets interrupted by Ctrl+C on the keyboard.
            BP.reset_all()                                  # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.

    def calibrate(self):                                    # Method for calibration of the band
 
        print('calibrating band...')
        BP.set_motor_dps(BP.PORT_B, -80)                    # Moving band forward until the light gray limiter touches the sensor

        try:
            value = BP.get_sensor(BP.PORT_2)
            while value != 1: 
                value = BP.get_sensor(BP.PORT_2)

            BP.set_motor_dps(BP.PORT_B, 0)
            BP.set_motor_dps(BP.PORT_B, 80)                 # Bringing the band to its initial position
            time.sleep(29)                                  # Travel time from sensor to initial position = 29s
            BP.set_motor_dps(BP.PORT_B, 0) 
            print('band calibrated!')
            
        except brickpi3.SensorError as error:
            BP.reset_all()
            print('error')
        except KeyboardInterrupt:                           # except the program gets interrupted by Ctrl+C on the keyboard.
            BP.reset_all()  



