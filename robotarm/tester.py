import crane
from crane import brick_pi
import time
if __name__ == "__main__":
    try:
        crane.initialize()  # Initialize BrickPi with its motors and sensors

        crane.calibration()  # Driving the robot to the normal position
        #crane.run_load()
       # time.sleep(3)
      #  crane.run_unload()
    finally:
        brick_pi.reset_all()
