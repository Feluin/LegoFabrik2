import time

from .motor import CalibratedMotor


class Forklift:
    """
    The bots forklift.
    """

    def __init__(self, bot):
        self._bot = bot

        self._rotate_motor = CalibratedMotor(
            CalibratedMotor._bp.PORT_B, calpow=70)
        self._height_motor = CalibratedMotor(
            CalibratedMotor._bp.PORT_A, calpow=60)

    def __del__(self):
        self._height_motor.to_init_position()

    def stop_all(self):
        """
        Stop rotation and height motor.
        """
        self._rotate_motor.stop()
        self._height_motor.stop()

    def calibrate(self):
        """
        Find minimum and maximum position for motors.
        """
        self._rotate_motor._pmin = self._rotate_motor._pinit = -300
        self._rotate_motor._pmax = 10603
        self._rotate_motor.to_init_position()

        self._height_motor.calibrate()

    def init_all(self):
        """
        Bring calibrated motors to init position.
        """
        self._rotate_motor.to_init_position()
        self._height_motor.to_init_position()

    def to_carry_mode(self):
        """
        Position forklift to carry an object around.
        """
        # rotate backwards
        self._rotate_motor.change_position(self._rotate_motor._pmax)
        time.sleep(1)
        # move fork up
        self._height_motor.change_position(self._height_motor.position_from_factor(-0.6))
        time.sleep(3)

    def to_pickup_mode(self):
        """
        Position forklift for picking up an object.
        """
        # rotate forward
        self._rotate_motor.to_init_position()

        # move fork down
        pos = self._height_motor.position_from_factor(-1.0)
        self._height_motor.change_position(pos)

    def set_custom_height(self, height):
        # rotate forward
        self._rotate_motor.to_init_position()
        # move fork on the right height
        height = ((height / 13.5) * 2) - 1
        # height = height / (maxHeight/2)-1
        pos = self._height_motor.position_from_factor(height)
        self._height_motor.change_position(pos)
