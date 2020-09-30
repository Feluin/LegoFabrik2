""" This file contains a class for controlling the motors of the truck. """

import time


class MotorController:
    """ Responsible for controlling the motors attached to the BrickPi 3. """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, brick_pi, motor_drive, motor_steer):
        self.brick_pi = brick_pi
        self.motor_drive = motor_drive
        self.motor_steer = motor_steer

        # target_power and current_power as percentage (-100 - 100)
        self.target_power = 0
        self.current_power = 0
        # change_delay in ms to increment or decrenent motor dps
        self.change_delay_ms = 20
        # last_change_time is the time in ns the motor
        # speed was changed the last time (e.g. while accelerating)
        self.last_change_time = 0
        # steering_limit will be set during motor_steering_calibration()
        # (e.g. 300 for a steering range between -300 and 300)
        self.steering_limit = 0

        brick_pi.set_motor_limits(motor_steer, 30)

    def steering_calibration(self):
        """ This function sets the motor encoder accordingly.
        It also centeres the steering. The steering should be
        done later with `motor_steer(direction)` """

        # Minimum change of rotary encoder per 100 ms to detect stall
        min_difference = 5
        # Calibration motor power in percentage (absolute)
        calibration_power = 30

        print('Calibration of steering axis started')
        current_pos = self.brick_pi.get_motor_encoder(self.motor_steer)
        last_pos = 99999999  # any super big number
        # Left turn calibration
        while abs(current_pos - last_pos) > min_difference:
            last_pos = current_pos
            self.brick_pi.set_motor_power(self.motor_steer, calibration_power)
            time.sleep(0.1)
            current_pos = self.brick_pi.get_motor_encoder(self.motor_steer)

        self.brick_pi.set_motor_power(self.motor_steer, 0)
        time.sleep(0.1)
        print('Reset motor encoder after left turn: 0')
        self.brick_pi.reset_motor_encoder(self.motor_steer)

        current_pos = self.brick_pi.get_motor_encoder(self.motor_steer)
        last_pos = 99999999  # any super big number
        # Right turn calibration
        while abs(current_pos - last_pos) > min_difference:
            last_pos = current_pos
            self.brick_pi.set_motor_power(self.motor_steer, -calibration_power)
            time.sleep(0.1)
            current_pos = self.brick_pi.get_motor_encoder(self.motor_steer)

        self.brick_pi.set_motor_power(self.motor_steer, 0)
        time.sleep(0.1)
        self.brick_pi.offset_motor_encoder(self.motor_steer, current_pos / 2)
        self.steering_limit = abs(
            self.brick_pi.get_motor_encoder(self.motor_steer))
        print('Offset motor encoder after right turn: ' +
              str(self.brick_pi.get_motor_encoder(self.motor_steer)))

        self.brick_pi.set_motor_position(self.motor_steer, 0)
        print('Calibration of steering axis completed')

    def steer(self, direction):
        """ This function allows a non blocking way to steer the truck.
        Only values between `-1` (left) and `1` (right) are allowed.
        Others are ignored! """

        if -1 <= direction <= 1:
            target_position = self.steering_limit * direction
            self.brick_pi.set_motor_position(
                self.motor_steer, -target_position)

    def loop(self):
        """ This function should be called every loop of the application.
        This ensures that the acceleration happens. The class properties
        `self.change_delay_ms`, `self.current_dps` and `self.target_dps`
        are used here! """

        # Current process time in milliseconds
        process_ms = time.process_time() * 1000

        if (process_ms - self.last_change_time) > self.change_delay_ms:
            self.last_change_time = process_ms
            # Acceleration
            if self.current_power < self.target_power:
                self.current_power += 5
                if self.current_power > self.target_power:  # fixes overshoot
                    self.current_power = self.target_power
            # Decelartion
            elif self.current_power > self.target_power:
                self.current_power -= 10  # Faster breaking of truck
                if self.current_power < 0:  # fixes negative power
                    self.current_power = 0
            self.brick_pi.set_motor_power(self.motor_drive, self.current_power)
