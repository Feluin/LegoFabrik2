import time

import cv2

from .forklift import Forklift
from .motor import CalibratedMotor, Motor


class Bot:
    """
    Control instance for a bot.
    """

    def __init__(self):
        self._drive_motor = Motor(Motor._bp.PORT_C)

        self._steer_motor = CalibratedMotor(Motor._bp.PORT_D, calpow=30)
        self._cap = None
        self._forklift = Forklift(self)
        self._sonar = None
        self.setup_cap()
        with open('/etc/hostname', 'r') as hostname:
            self._name = hostname.read().strip()

    def name(self):
        """
        Returns the bot hostname.
        """
        return self._name

    def setup_broker(self, subscriptions=None):
        from .broker import Broker
        """
        Initialize a `Broker` connection.
        """
        self._broker = Broker(self, subscriptions)

    def detect_object(self, cascade: str):
        """
        Detect Objects
        """
        from .objectDetection import ObjectDetection
        detection = ObjectDetection(self)
        return detection.detect(cascade)

    def get_cap(self) -> cv2.VideoCapture:
        if self._cap is None:
            self._cap = cv2.VideoCapture(-1)
        return self._cap.read()

    def setup_cap(self):
        """
        Initialize a `Cap` object.
        """
        self._cap = cv2.VideoCapture(0)

    def drive_power(self, pnew):
        """
        Set the driving power

        :param pnew: a value between -100 and 100.
        """
        self._drive_motor.change_power(pnew)

    def drive_steer(self, pnew):
        """
        Set the steering position.

        :param pnew: a value between -1.0 and 1.0.
        """
        pos = self._steer_motor.position_from_factor(pnew)
        self._steer_motor.change_position(pos)

    def calibrate(self):
        """
        Find minimum and maximum position for motors.
        """
        self._steer_motor.calibrate()
        self._forklift.calibrate()

    def sonar(self):
        """
        Initialize a `Sonar` object.

        :return: A `Sonar` instance.
        """
        if self._sonar == None:
            from .sonar import Sonar
            self._sonar = Sonar()
        return self._sonar

    def stop_all(self):
        """
        Stop driving and steering motor as well as `Forklift`.
        """
        self._drive_motor.stop()
        self._steer_motor.stop()
        self._forklift.stop_all()

    def stop_and_init_all(self):
        """
        Stop driving and steering motor as well as `Forklift` and set them to init position.
        """
        self.stop_all()
        self._steer_motor.to_init_position()
        self._forklift.init_all()

    # -1 =left 1= right
    def steer(self, posfactor):
        """ """
        diff = self._steer_motor.currentpos - posfactor
        if (diff > 0):
            self._steer_motor.change_position(
                self._steer_motor.position_from_factor(posfactor - 0.1))
        elif diff < 0:
            self._steer_motor.change_position(
                self._steer_motor.position_from_factor(posfactor + 0.1))
        time.sleep(1)
        self._steer_motor.change_position(
            self._steer_motor.position_from_factor(posfactor))

    def stop_moving(self):
        self._drive_motor.change_power(0)
        self._steer_motor.change_position(
            self._steer_motor.position_from_factor(0))
        time.sleep(1)

    def setMoving(self, power, secs=2.0):
        print("started")
        self._drive_motor.change_power(power)
        time.sleep(secs)
        self._drive_motor.change_power(0)
        print("stopped")
