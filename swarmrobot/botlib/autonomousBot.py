import logging
import threading
import time

import numpy as np

from .bot import Bot
from .enum_storageContainerPosition import StorageContainerPosition
from .lineDetection import LineTracking
from .objectDetection import ObjectDetection


class AutonomousBot(Bot):
    """
    Control instance for a autonomous bot.
    """

    def __init__(self):
        super().__init__()
        self.calibrate()

        # Global variable for storing last image from camera thread
        self._current_image = None
        # Global flag to pause line detection
        self._pause_line_detection = False
        # Global variable for storing last ultra sonic measurements
        # Order of sonic sensors: [LEFT, LEFT45, LEFT_FRONT, RIGHT_FRONT, RIGHT45, RIGHT]
        self._sonic_data = [None, None, None, None, None, None]
        # Global variable for frontward speed of rorbot (adjust carefully since the image-processing-power is limited)
        self._speed = 25
        # Global flag for line detection
        self._status_line_detected = False
        # Global flag for parking slot detection
        self._status_parking_slot_detected = False
        # Global flag for stop sign detection
        self._status_stop_sign_detected = False
        # Global flag for storage container detection
        self._status_storage_container_detected = False
        # Global flag which stops all detections threads when set
        self._stop = False

        self._threads = list()

        # Create and start the image capture thread
        logging.info(
            "AutonomousBot : create and start image_capture thread")
        imageCaptureThread = threading.Thread(
            target=self.start_image_capture, name='image_capture', args=(), daemon=True)
        self._threads.append(imageCaptureThread)
        imageCaptureThread.start()

        # Time to boot the camera and to take the first image
        time.sleep(1)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Stop all threads
        self._stop = True

        # Stop all motors and bring them into the init-position
        self.stop_and_init_all()

        # Wait until all running threads are terminated
        for _, thread in enumerate(self._threads):
            thread.join()
            logging.info("AutonomousBot : thread %s done", thread.getName())

    def start_image_capture(self):
        """
        Capture an image and saves it in the class attribute [_current_image].
        """
        while not self._stop:
            _, self._current_image = self.get_cap()

    def start_line_detection(self):
        """
        Detect line in image from class attribute [_current_image].
        """
        last_detected_time = 0

        while not self._stop:
            lt = LineTracking()
            coords, _ = lt.track_line(self._current_image.copy())
            last_detected_time_difference = int(
                round(time.time() * 1000)) - last_detected_time

            # If line coordinates are detected.
            if coords != None and not self._pause_line_detection:
                last_detected_time = int(round(time.time() * 1000))
                self._status_line_detected = True
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
                self._drive_motor.change_power(0)
                self._steer_motor.change_position(
                    self._steer_motor.position_from_factor(0))
                self._status_line_detected = False
                logging.info(
                    "AutonomousBot:LineDetection : no line detected")
                break

    def start_parking_slot_detection(self):
        """
        Detect parking slot in image from class attribute [_current_image].
        """
        # Buffer to prevent fast switching back and forth of global flag variable
        counter = 0

        while not self._stop:
            od = ObjectDetection()

            status_parking_slot, _ = od.detect_parking_slot(
                self._current_image.copy())

            if status_parking_slot:
                counter = 0
                if self._status_parking_slot_detected != status_parking_slot:
                    logging.info(
                        "AutonomousBot:ParkingSlotDetection : parking slot detected.")
                # Sets global flag to True
                self._status_parking_slot_detected = status_parking_slot

            elif counter >= 7:
                self.start_parking_slot_detection = False
                counter = counter + 1

            else:
                counter = counter + 1

    def start_sonar_detection(self):
        """
        Get actual sonar data and calculates the median from the last five measurements to flatten peaks / wrong measurements.
        """
        buffer_left = list()
        buffer_left_front = list()
        buffer_right = list()
        buffer_right_45 = list()
        buffer_right_front = list()

        while not self._stop:
            # Add the new measurements to the specific buffer list
            buffer_left.append(
                self.sonar().read(self.sonar().LEFT))
            buffer_left_front.append(
                self.sonar().read(self.sonar().LEFT_FRONT))
            buffer_right.append(
                self.sonar().read(self.sonar().RIGHT))
            buffer_right_45.append(
                self.sonar().read(self.sonar().RIGHT45))
            buffer_right_front.append(
                self.sonar().read(self.sonar().RIGHT_FRONT))

            # Remove oldest measurement (when maximum of five is reached)
            if len(buffer_left) > 5:
                buffer_left.pop(0)
            if len(buffer_left_front) > 5:
                buffer_left_front.pop(0)
            if len(buffer_right) > 5:
                buffer_right.pop(0)
            if len(buffer_right_45) > 5:
                buffer_right_45.pop(0)
            if len(buffer_right_front) > 5:
                buffer_right_front.pop(0)

            # Calculate the median from each buffer list and saves them in class attribute
            self._sonic_data = [np.nanmedian(buffer_left), None, np.nanmedian(
                buffer_left_front), np.nanmedian(buffer_right_front), np.nanmedian(buffer_right_45), np.nanmedian(buffer_right)]

    def start_stop_sign_detection(self):
        """
        Detect stop sign in image from class attribute [_current_image].
        """
        last_detected_time = 0

        while not self._stop:
            last_detected_time_difference = int(
                round(time.time() * 1000)) - last_detected_time
            od = ObjectDetection()

            status_stop_sign, _ = od.detect_stop_sign(
                self._current_image.copy())

            if status_stop_sign:
                last_detected_time = int(round(time.time() * 1000))
                # If stop sign is detected and now stop sign was detected in the past 2 seconds
                if self._status_stop_sign_detected != status_stop_sign and last_detected_time_difference >= 2000:
                    logging.info(
                        "AutonomousBot:StopSignDetection : stop sign detected.")
                    self._status_stop_sign_detected = status_stop_sign
            else:
                self._status_stop_sign_detected = False

    def start_storage_container_detection(self):
        """
        Detect storage container in image from class attribute [_current_image].
        """
        while not self._stop:
            od = ObjectDetection()
            # Buffer to prevent fast switching back and forth of global flag variable
            counter = 0

            status_storage_container, _ = od.detect_storage_container(
                self._current_image.copy())

            if status_storage_container:
                counter = 0
                if self._status_storage_container_detected != status_storage_container:
                    logging.info(
                        "AutonomousBot:StorageContainerDetection : storage container detected.")
                # Set global flag to True
                self._status_storage_container_detected = status_storage_container

            elif counter >= 7:
                self._status_storage_container_detected = False
                counter = counter + 1

            else:
                counter = counter + 1

    def start_detection_thread(self, function, is_daemon=True):
        """
        Create and start a thread for detecting functions.

        :param function: Function for the new thread to execute.
        """
        logging.info(
            "AutonomousBot : create and start %s thread", function.__name__.split("start_", 1)[1])

        # Create new thread
        detectionThread = threading.Thread(
            target=function, name=function.__name__.split("start_", 1)[1], args=(), daemon=is_daemon)

        # Append the thread to global threadlist
        self._threads.append(detectionThread)

        # Start the created thread
        detectionThread.start()

    def restart_detection_thread(self, function):
        """
        Join old thread, create and start a new thread for detecting functions.

        :param function: Function for the new thread to execute.
        """

        # Searche and join the thread with the specified function (parameter)
        for _, thread in enumerate(self._threads):
            if thread.getName() == function.__name__.split("start_", 1)[1]:
                thread.join()
                logging.info("AutonomousBot : thread %s done",
                             thread.getName())

        # Start a new thread with the specified function (parameter)
        self.start_detection_thread(function)

    def start(self):
        """
        Start all detecting functions in different threads.
        """
        self._stop = False
        self.start_detection_thread(self.start_sonar_detection)
        # Time to boot the ultrasonic sensors and to take first measurements
        time.sleep(1)
        self.start_detection_thread(self.start_line_detection)
        self.start_detection_thread(self.start_parking_slot_detection)
        self.start_detection_thread(self.start_stop_sign_detection)
        self.start_detection_thread(self.start_storage_container_detection)

        while not self._stop:
            # Stop sign handling
            if self._status_stop_sign_detected:
                # Stop the forward driving
                temp_speed = self._speed
                self._speed = 0
                self._drive_motor.change_power(0)
                logging.info(
                    "AutonomousBot:StopSignDetection : successfully stopped at stop sign")

                # Wait two seconds
                time.sleep(2)

                # Continue the driving
                self._speed = temp_speed
                self._status_stop_sign_detected = False

            # Right of way and storage container handling (Checking Sonic.LEFT_FRONT, Sonic.RIGHT_FRONT, Sonic.RIGHT45)
            elif (self._sonic_data[2] < 30 if self._sonic_data[2] != None else False) or (self._sonic_data[3] < 30 if self._sonic_data[3] != None else False) or (self._sonic_data[4] < 50 if self._sonic_data[4] != None else False):
                while True:
                    # Stop the forward driving and pause line detection
                    self._pause_line_detection = True
                    temp_speed = self._speed
                    self._speed = 0
                    self._drive_motor.change_power(0)

                    # If no storage container and objekt from RIGHT45-sensor is detected, start right of way handling
                    if not self._status_storage_container_detected and (self._sonic_data[4] < 50 if self._sonic_data[4] != None else True):
                        logging.info(
                            "AutonomousBot:StopSignDetection : successfully stopped for right of way order")

                        # Wait until way is free
                        while (self._sonic_data[2] < 30 if self._sonic_data[2] != None else False) or (self._sonic_data[3] < 30 if self._sonic_data[3] != None else False) or (self._sonic_data[4] < 40 if self._sonic_data[4] != None else False):
                            time.sleep(1)

                        # Continue driving
                        self._speed = temp_speed
                        self._pause_line_detection = False

                    # Is storage container is detected, start handling
                    elif self._status_storage_container_detected:
                        # Bring forklift motors into loading position
                        self._forklift._rotate_motor.to_init_position()
                        self._forklift._height_motor.change_position(
                            self._forklift._height_motor.position_from_factor(StorageContainerPosition.WhiteBox.value))

                        # Drive slowly to storage container
                        while self._sonic_data[2] > 10 and self._sonic_data[3] > 10:
                            self._drive_motor.change_power(18)

                        # Pick up storage container
                        self._drive_motor.change_power(0)
                        self._forklift._height_motor.change_position(
                            self._forklift._height_motor.position_from_factor(StorageContainerPosition.WhiteBox.value + 0.2))
                        self._forklift._rotate_motor.change_position(
                            self._forklift._rotate_motor._pmax)
                        # Wait for motors to pick up storage container
                        time.sleep(7)

                        # Drive backward
                        while self._sonic_data[2] < 40 or self._sonic_data[3] < 40:
                            self._drive_motor.change_power(-20)

                        logging.info(
                            "AutonomousBot:StorageContainerDetection : successfully picked up storage container")
                        self._stop = True
                        break

            # Parking slot handling
            elif not self._status_line_detected and self._status_parking_slot_detected:
                self._steer_motor.change_position(
                    self._steer_motor.position_from_factor(0))
                self._drive_motor.change_power(self._speed)
                time.sleep(3)
                self._drive_motor.change_power(0)
                logging.info(
                    "AutonomousBot:ParkingSlotDetection : successfully parked in parking slot")
                self._stop = True


if __name__ == '__main__':
    with AutonomousBot() as bot:
        bot.start()
