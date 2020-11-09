import logging
import time

from .autonomousBot import SwarmLabBot

from .lineDetection import LineTracking

"""
The bot for the Swarmlabsimulation 
"""


class SwarmLabBot(SwarmLabBot):

    def setup(self):
        self._stop = False

        self.start_detection_thread(self.start_sonar_detection)
        # Time to boot the ultrasonic sensors and to take first measurements
        time.sleep(1)

    def __init__(self):
        super().__init__()
        self._speed_slow = 21
        self._speed_max = 33

    """
    moving from starting pos to Warehouse along  a line 
    """

    def moveToWarehouse(self, startingpos=1):
        if (startingpos == 2):
            self.setMoving(secs=1, power=self._speed_max)
            self.steer(-0.9)
            self.setMoving(secs=5, power=self._speed)
            self.steer(0)
            self.setMoving(secs=1, power=self._speed)
            self.steer(0.5)
            self._drive_motor.change_power(self._speed)
            time.sleep(6)

        self.moveAlongLine(widthToObstacle=35, rightbeforeleft=True)
        time.sleep(1)

    """
    Handling detected Stopsign
     """

    def handleStopSign(self):
        # Stop the forward driving
        temp_speed = self._speed
        self._speed = 0
        self._drive_motor.change_power(0)
        logging.info(
            "SwarmlabBot:StopSignDetection : successfully stopped at stop sign")

        # Wait two seconds
        time.sleep(2)

        # Continue the driving
        self._speed = temp_speed
        self._status_stop_sign_detected = False

    """
    moving along A Black line on White ground
    @obstacledetection= allow sonic sensors to stop the movement
    @widthToObstacle= distance to the obstacle until it stops
    @rightbeforeleft =handling right before left 
    """

    def moveAlongLine(self, obstacledetection=True, widthToObstacle=55, rightbeforeleft=False):
        linefound = False
        print("Moving along line")
        last_detected_time = 0
        while not self._stop:
            time.sleep(0.1)
            lt = LineTracking()
            coords, _ = lt.track_line(self._current_image.copy())
            last_detected_time_difference = int(
                round(time.time() * 1000)) - last_detected_time

            if rightbeforeleft and self._sonic_data[4] < 50 if self._sonic_data[4] != None else False:
                self._drive_motor.change_power(0)
                self._steer_motor.change_position(
                    self._steer_motor.position_from_factor(0))
                time.sleep(1)
                if self._sonic_data[4] < 50 if self._sonic_data[4] != None else False:
                    time.sleep(10)

            # break iftheres a obstacle
            if obstacledetection and (
                    (self._sonic_data[2] < widthToObstacle if self._sonic_data[2] != None else False) or (
                    self._sonic_data[3] < widthToObstacle if self._sonic_data[3] != None else False)):
                self._drive_motor.change_power(0)
                self._steer_motor.change_position(
                    self._steer_motor.position_from_factor(0))
                time.sleep(2)
                if (self._sonic_data[2] < widthToObstacle if self._sonic_data[2] != None else False) or (
                        self._sonic_data[3] < widthToObstacle if self._sonic_data[3] != None else False):
                    print("obstacle in font: " + str(self._sonic_data[2]) + " " + str(self._sonic_data[3]))
                    self._steer_motor.change_position(
                        self._steer_motor.position_from_factor(0))
                    self._drive_motor.change_power(0)

                    return
                else:
                    self._drive_motor.change_power(self._speed)

            # If line coordinates are detected.
            if coords != None and not self._pause_line_detection:
                last_detected_time = int(round(time.time() * 1000))
                self._status_line_detected = True
                if linefound == False:
                    print("Line found")
                linefound = True
                delta = -160 + coords[2]
                # If delta out of tolerance, steer right
                if (delta > 10):
                    self._drive_motor.change_power(self._speed)
                    self._steer_motor.change_position(
                        self._steer_motor.position_from_factor(coords[2] / 320))

                # Else if delta out of tolerance, steer left
                elif delta < -10:
                    self._drive_motor.change_power(self._speed)
                    self._steer_motor.change_position(
                        self._steer_motor.position_from_factor(-(160 - coords[2]) / 160))

                # Else drive streight
                else:
                    self._drive_motor.change_power(self._speed)
                    self._steer_motor.change_position(
                        self._steer_motor.position_from_factor(0))

            # If no line is detected stop driving
            elif not self._pause_line_detection:
                # if there is no line found, continue driving
                if linefound == False:
                    continue
                # if there was a line and it ended , do the next step
                self._drive_motor.change_power(0)
                self._steer_motor.change_position(
                    self._steer_motor.position_from_factor(0))
                print("no line")
                return

    """picking storage up from warehouse"""

    def handleWarehouse(self):
        self.steer(0.0)
        self.setMoving(0, 1)
        while self._sonic_data[2] > 22 or self._sonic_data[3] > 22:
            print(self._sonic_data[2] - self._sonic_data[3])
            if 1 > abs(self._sonic_data[2] - self._sonic_data[3]):
                self._drive_motor.change_power(self._speed_slow)
                self._steer_motor.change_position(
                    self._steer_motor.position_from_factor(0))
            elif self._sonic_data[2] > self._sonic_data[3]:
                self._steer_motor.change_position(
                    self._steer_motor.position_from_factor(0.2))
                self._drive_motor.change_power(self._speed_slow)
            # Else if delta out of tolerance, steer left
            else:
                self._steer_motor.change_position(
                    self._steer_motor.position_from_factor(-0.2))
                self._drive_motor.change_power(self._speed_slow)
            time.sleep(0.2)
        self.setMoving(0, 1)
        self._forklift.to_pickup_mode()
        self._forklift.set_custom_height(9.7)
        time.sleep(4)
        self.steer(0.0)
        time.sleep(1)
        self._drive_motor.change_power(self._speed_max)
        time.sleep(2)
        self._drive_motor.change_power(0)
        self._forklift.set_custom_height(12)
        time.sleep(2)
        self._drive_motor.change_power(-self._speed_slow)
        time.sleep(3)
        self._drive_motor.change_power(0)
        self._forklift.to_carry_mode()

    """ move back until the swarm robot is parallel to an obstacle in front"""

    def anlignobstacle(self):
        while 2 < abs(self._sonic_data[2] - self._sonic_data[3]) < 10:
            if self._sonic_data[2] < self._sonic_data[3]:
                self._drive_motor.change_power(-self._speed_slow)
                self._steer_motor.change_position(
                    self._steer_motor.position_from_factor(0.7))
            # Else if delta out of tolerance, steer left
            else:
                self._drive_motor.change_power(-self._speed_slow)
                self._steer_motor.change_position(
                    self._steer_motor.position_from_factor(-0.7))
        self._drive_motor.change_power(0)
        self._steer_motor.change_position(
            self._steer_motor.position_from_factor(0))
        return

    """Move from Warehouse to the sorting factory """

    def moveToSortingFactory(self):
        self._steer_motor.change_position(
            self._steer_motor.position_from_factor(0.8))
        self._drive_motor.change_power(-self._speed)
        time.sleep(3.5)
        self._drive_motor.change_power(0)
        self._steer_motor.change_position(
            self._steer_motor.position_from_factor(0))
        time.sleep(1.5)
        self._steer_motor.change_position(
            self._steer_motor.position_from_factor(-0.35))
        self._drive_motor.change_power(self._speed)
        time.sleep(2.5)
        self._drive_motor.change_power(0)
        # stap
        time.sleep(3)
        self._drive_motor.change_power(self._speed)
        time.sleep(3)
        self.steer(0)
        self.setMoving(1.5, secs=1)

        self.moveAlongLine(widthToObstacle=45)

    """Unload the pallet at the sorting factory """

    def unload_sorting_Factory(self):
        self._forklift.set_custom_height(9)
        self._drive_motor.change_power(self._speed)
        time.sleep(5)
        self._drive_motor.change_power(0)
        self._forklift.set_custom_height(5)
        time.sleep(3)
        self._drive_motor.change_power(-self._speed_max)
        time.sleep(3)
        self._drive_motor.change_power(0)

    """Move from sortinginput to output """

    def moveToSortingOutput(self):
        self._steer_motor.change_position(
            self._steer_motor.position_from_factor(0.8))
        self._drive_motor.change_power(-self._speed)
        time.sleep(3)
        self._drive_motor.change_power(0)
        self._steer_motor.change_position(
            self._steer_motor.position_from_factor(0))

        time.sleep(1)
        self._drive_motor.change_power(-self._speed)
        time.sleep(0.5)
        self._drive_motor.change_power(0)
        time.sleep(1)
        self._steer_motor.change_position(
            self._steer_motor.position_from_factor(-0.8))
        self._drive_motor.change_power(-self._speed)
        time.sleep(3)
        self._steer_motor.change_position(
            self._steer_motor.position_from_factor(0))
        self._drive_motor.change_power(0)
        self.moveAlongLine(widthToObstacle=45)

    """Move from sortingoutput to the robotarm with the Truck """

    def move_toRobotarm(self):
        self._forklift.to_carry_mode()
        self._steer_motor.change_position(
            self._steer_motor.position_from_factor(0.8))
        self._drive_motor.change_power(-self._speed)
        time.sleep(2)
        self._drive_motor.change_power(0)

        time.sleep(1)
        self._steer_motor.change_position(
            self._steer_motor.position_from_factor(-0.8))
        self._drive_motor.change_power(self._speed)
        time.sleep(5.5)
        self.setMoving(power=0, secs=2)

    """Unload at the Robotarm """

    def unload_Robotarm(self):
        self.moveAlongLine(widthToObstacle=45)
        self._steer_motor.change_position(
            self._steer_motor.position_from_factor(0))
        time.sleep(1)
        self.moveStraightUntilObstacle(widthToObstacle=38, activateLeft=False, speed=22)
        self._drive_motor.change_power(0)
        self._forklift.set_custom_height(0)
        time.sleep(7)
        self._drive_motor.change_power(-self._speed)
        time.sleep(2)
        self._drive_motor.change_power(0)

    """Pickup the pallet from the Robotarm """

    def pickup_pallet_from_robotarm(self):
        self.steer(-0.1)
        self._drive_motor.change_power(self._speed)
        time.sleep(2.5)
        self._drive_motor.change_power(0)
        self._forklift.to_carry_mode()
        time.sleep(5)
        self._drive_motor.change_power(-self._speed)
        time.sleep(3)
        self._drive_motor.change_power(0)

    """Pickup the pallet from the Sorting machine output """

    def pickup_Pallet_from_SortingMachine(self):
        self._forklift.set_custom_height(0)
        time.sleep(2.5)
        self._drive_motor.change_power(self._speed)
        time.sleep(0.5)

        self._drive_motor.change_power(self._speed)
        time.sleep(3)
        self._drive_motor.change_power(0)
        self._forklift.to_carry_mode()
        time.sleep(4)
        self._drive_motor.change_power(-self._speed)
        time.sleep(1)
        self._drive_motor.change_power(0)

    """ Moves in a straight line to the obstacle"""

    def moveStraightUntilObstacle(self, widthToObstacle=50.0, activateLeft=True, activateRight=True, speed=25):
        self._steer_motor.change_position(
            self._steer_motor.position_from_factor(0))
        while ((self._sonic_data[2] > widthToObstacle if self._sonic_data[
                                                             2] is not None else False) and activateLeft) or (
                (
                        self._sonic_data[3] > widthToObstacle if self._sonic_data[
                                                                     3] is not None else False) and activateRight):
            time.sleep(0.1)
            print(self._sonic_data)
            if ((self._sonic_data[2] < widthToObstacle if self._sonic_data[
                                                              2] is not None else False) and activateLeft) or (
                    (self._sonic_data[3] < widthToObstacle if self._sonic_data[
                                                                  3] is not None else False) and activateLeft):
                logging.info("obstacle detected")
                self._steer_motor.change_position(
                    self._steer_motor.position_from_factor(0))
                self._drive_motor.change_power(0)
                return
            else:
                self._drive_motor.change_power(speed)
        logging.info("obstacle detected")
        self._drive_motor.change_power(0)

    """ Moves from the Robotarm away"""
    def moveFromArmAway(self):
        self._steer_motor.change_position(
            self._steer_motor.position_from_factor(0.8))
        self._drive_motor.change_power(-self._speed)
        time.sleep(4)
        self._drive_motor.change_power(0)
        self._steer_motor.change_position(
            self._steer_motor.position_from_factor(0))
        time.sleep(1)
        self._drive_motor.change_power(self._speed)
        time.sleep(3)
        self.moveAlongLine(obstacledetection=False)

    """ Bring the pallet back to the warehouse """
    def deliverPalletatwarehouse(self):
        self.steer(-0.2)
        self._drive_motor.change_power(25)
        time.sleep(4)
        self.moveAlongLine()
        self.steer(0.8)
        self._drive_motor.change_power(-self._speed)
        time.sleep(5)
        self.moveAlongLine(widthToObstacle=45)

    """ Unload the pallet at the warehouse """
    def unload_at_warehouse(self):
        self._forklift.set_custom_height(12)
        time.sleep(5)
        while self._sonic_data[2] > 20 or self._sonic_data[3] > 20:
            print(self._sonic_data[2] - self._sonic_data[3])
            if 1 > abs(self._sonic_data[2] - self._sonic_data[3]):
                self._drive_motor.change_power(23)
                self._steer_motor.change_position(
                    self._steer_motor.position_from_factor(0))
            elif self._sonic_data[2] > self._sonic_data[3]:
                self._steer_motor.change_position(
                    self._steer_motor.position_from_factor(0.2))
                self._drive_motor.change_power(23)
            # Else if delta out of tolerance, steer left
            else:
                self._steer_motor.change_position(
                    self._steer_motor.position_from_factor(-0.2))
                self._drive_motor.change_power(23)
            time.sleep(0.4)
        self._drive_motor.change_power(0)
        self._steer_motor.change_position(
            self._steer_motor.position_from_factor(0))
        time.sleep(0.5)
        self._drive_motor.change_power(self._speed_max)
        time.sleep(3)
        self._drive_motor.change_power(0)
        self._forklift.set_custom_height(9.3)
        time.sleep(2)
        self._drive_motor.change_power(-23)
        time.sleep(3)
        self._drive_motor.change_power(0)
        self._forklift.to_carry_mode()

    """ 
    Moving back to the parking spot 
    """
    def move_to_Parkingspot(self):
        self.steer(0.8)
        self.setMoving(power=-self._speed, secs=5.6)
        self.steer(-0.8)
        self.setMoving(secs=2, power=self._speed)
        self.steer(0)
        self.setMoving(secs=3, power=self._speed)
        self.steer(-0.8)
        self._drive_motor.change_power(self._speed)
        time.sleep(4.5)
        self.moveAlongLine(obstacledetection=False)
        time.sleep(2)
        self.steer(-0.8)
        self.setMoving(secs=12, power=self._speed)
        self.steer(0.5)
        self.setMoving(secs=3, power=-self._speed)
        self.steer(-0.3)
        self.setMoving(secs=3, power=self._speed)
