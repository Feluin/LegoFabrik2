""" This file is for controlling the robotarm. """

# Import system libraries
import sys
import time
import threading

# Import third-party libraries
import brickpi3
# Needed here for constant definitions
brick_pi = brickpi3.BrickPi3()

# Ports for motor connection
MOTOR_VERTICAL_AXIS = brick_pi.PORT_A
MOTOR_HORIZONTAL_AXIS = brick_pi.PORT_B
MOTOR_ROTATION_AXIS = brick_pi.PORT_D
MOTOR_GRIPPER = brick_pi.PORT_C

# Motor power limits in percentage
MOTOR_VERTICAL_AXIS_LIMIT = 30
MOTOR_HORIZONTAL_AXIS_LIMIT = 40
MOTOR_ROTATION_AXIS_LIMIT = 100
MOTOR_GRIPPER_LIMIT = 100

# Ports for sensor connection
SENSOR_VERTICAL_AXIS = brick_pi.PORT_1
SENSOR_HORIZONTAL_AXIS = brick_pi.PORT_2
SENSOR_ROTATION_AXIS = brick_pi.PORT_4
SENSOR_GRIPPER = brick_pi.PORT_3


def read_sensor(sensor):
    """ Helper function to read a sensor value and handle possible errors. """

    try:
        value = brick_pi.get_sensor(sensor)
        return value
    except brickpi3.SensorError as error:
        print(error)
        return 0


def initialize():
    """ Configuration of the Brick Pi and all connected motors / sensors. """

    brick_pi.set_sensor_type(SENSOR_VERTICAL_AXIS, brick_pi.SENSOR_TYPE.TOUCH)
    brick_pi.set_sensor_type(SENSOR_HORIZONTAL_AXIS,
                             brick_pi.SENSOR_TYPE.TOUCH)
    brick_pi.set_sensor_type(SENSOR_ROTATION_AXIS, brick_pi.SENSOR_TYPE.TOUCH)
    brick_pi.set_sensor_type(SENSOR_GRIPPER, brick_pi.SENSOR_TYPE.TOUCH)

    brick_pi.set_motor_limits(MOTOR_VERTICAL_AXIS, MOTOR_VERTICAL_AXIS_LIMIT)
    brick_pi.set_motor_limits(MOTOR_HORIZONTAL_AXIS,
                              MOTOR_HORIZONTAL_AXIS_LIMIT)
    brick_pi.set_motor_limits(MOTOR_ROTATION_AXIS, MOTOR_ROTATION_AXIS_LIMIT)
    brick_pi.set_motor_limits(MOTOR_GRIPPER, MOTOR_GRIPPER_LIMIT)


def calibration():
    """ Calibrates all motors to the normal position using the sensors.
    Should be run at least once at the start of the program. """

    global currently_running
    print("Calibration of robot arm started")

    # Reset vertical axis
    while read_sensor(SENSOR_VERTICAL_AXIS) == 0:
        brick_pi.set_motor_power(MOTOR_VERTICAL_AXIS, 30)
        time.sleep(0.02)  # Reduce CPU load
    brick_pi.set_motor_power(MOTOR_VERTICAL_AXIS, 0)
    time.sleep(1)  # Let motor break

    # Reset horizontal axis
    while read_sensor(SENSOR_HORIZONTAL_AXIS) == 0:
        brick_pi.set_motor_power(MOTOR_HORIZONTAL_AXIS, -80)
        time.sleep(0.02)  # Reduce CPU load
    brick_pi.set_motor_power(MOTOR_HORIZONTAL_AXIS, 0)
    time.sleep(1)  # Let motor break

    # Reset rotation axis
    brick_pi.set_motor_position_relative(MOTOR_ROTATION_AXIS, -1000)
    time.sleep(2.5)
    while read_sensor(SENSOR_ROTATION_AXIS) == 0:
        brick_pi.set_motor_power(MOTOR_ROTATION_AXIS, 100)
        time.sleep(0.02)  # Reduce the Raspberry Pi CPU load.
    brick_pi.set_motor_power(MOTOR_ROTATION_AXIS, 0)
    time.sleep(0.05)  # Let motor break

    # Turn rotational axis
    brick_pi.set_motor_position_relative(MOTOR_ROTATION_AXIS, -3200)

    # Drive down horizontal axis
    brick_pi.set_motor_position_relative(MOTOR_HORIZONTAL_AXIS, 750)

    # Reset gripper
    while read_sensor(SENSOR_GRIPPER) == 0:
        brick_pi.set_motor_power(MOTOR_GRIPPER, -100)
        time.sleep(0.02)  # Reduce the Raspberry Pi CPU load.
    brick_pi.set_motor_power(MOTOR_GRIPPER, 0)
    time.sleep(1)  # Let motor break
    # Open gripper (not fully because sensor is centered)
    brick_pi.set_motor_position_relative(MOTOR_GRIPPER, 9000)
    time.sleep(8)  # Let motor break

    currently_running = False
    print("Calibration of robot arm completed")


def run_load():
    """ Used to load the palett from the ground to the truck. """
    # Protection against running multiple times
    global currently_running
    if currently_running:
        return
    currently_running = True
    print("Loading of truck strated")

    # Drive down horizontal axis
    brick_pi.set_motor_position_relative(MOTOR_HORIZONTAL_AXIS, 1550)

    # Drive down vertical axis
    brick_pi.set_motor_position_relative(MOTOR_VERTICAL_AXIS, -840)
    time.sleep(5)  # Let motor run

    # Close gripper
    brick_pi.set_motor_position_relative(MOTOR_GRIPPER, -12000)
    time.sleep(9)  # Let motor run

    # Drive up horizontal axis
    brick_pi.set_motor_position_relative(MOTOR_HORIZONTAL_AXIS, -1590)

    # Reset vertical axis
    while read_sensor(SENSOR_VERTICAL_AXIS) == 0:
        brick_pi.set_motor_power(MOTOR_VERTICAL_AXIS, 30)
        time.sleep(0.02)  # Reduce CPU load
    brick_pi.set_motor_power(MOTOR_VERTICAL_AXIS, 0)
    time.sleep(1)  # Let motor break

    # Reset rotation axis and turn to truck
    while read_sensor(SENSOR_ROTATION_AXIS) == 0:
        brick_pi.set_motor_power(MOTOR_ROTATION_AXIS, 100)
        time.sleep(0.02)  # Reduce the Raspberry Pi CPU load.
    brick_pi.set_motor_power(MOTOR_ROTATION_AXIS, 0)
    time.sleep(0.05)  # Let motor break
    brick_pi.set_motor_position_relative(MOTOR_ROTATION_AXIS, -60)
    time.sleep(1)  # Let motor break

    # Drive down vertical axis
    brick_pi.set_motor_position_relative(MOTOR_VERTICAL_AXIS, -960)
    time.sleep(4)  # Let motor run

    # Drive down horizontal axis
    brick_pi.set_motor_position_relative(MOTOR_HORIZONTAL_AXIS, 540)
    time.sleep(2)  # Let motor run

    # Open gripper
    brick_pi.set_motor_position_relative(MOTOR_GRIPPER, 12000)
    time.sleep(9)  # Let motor run

    # Drive up horizontal axis
    brick_pi.set_motor_position_relative(MOTOR_HORIZONTAL_AXIS, -620)

    # Reset vertical axis
    while read_sensor(SENSOR_VERTICAL_AXIS) == 0:
        brick_pi.set_motor_power(MOTOR_VERTICAL_AXIS, 30)
        time.sleep(0.02)  # Reduce CPU load
    brick_pi.set_motor_power(MOTOR_VERTICAL_AXIS, 0)
    time.sleep(0.05)  # Let motor break

    # Start truck
    mqtt_client.publish(MQTT_TOPIC_PUBLISH, MQTT_MESSAGE_PUBLISH, 1)
    time.sleep(2)

    # Turn rotation axis
    brick_pi.set_motor_position_relative(MOTOR_ROTATION_AXIS, -3140)

    # Reset horizontal axis
    while read_sensor(SENSOR_HORIZONTAL_AXIS) == 0:
        brick_pi.set_motor_power(MOTOR_HORIZONTAL_AXIS, -80)
        time.sleep(0.02)  # Reduce CPU load
    brick_pi.set_motor_power(MOTOR_HORIZONTAL_AXIS, 0)
    time.sleep(1)  # Let motor break

    # Drive down horizontal axis
    brick_pi.set_motor_position_relative(MOTOR_HORIZONTAL_AXIS, 750)
    time.sleep(2)  # Let motor break

    print("Loading of truck finished")
    currently_running = False


def run_unload():
    """ Used to unload the palett from the truck to the ground. """

    # Protection against running multiple times
    global currently_running
    if currently_running:
        return
    currently_running = True
    print("Unloading of truck strated")

    # Reset rotation axis and turn to truck
    while read_sensor(SENSOR_ROTATION_AXIS) == 0:
        brick_pi.set_motor_power(MOTOR_ROTATION_AXIS, 100)
        time.sleep(0.02)  # Reduce the Raspberry Pi CPU load.
    brick_pi.set_motor_power(MOTOR_ROTATION_AXIS, 0)
    time.sleep(0.05)  # Let motor break
    brick_pi.set_motor_position_relative(MOTOR_ROTATION_AXIS, -60)
    time.sleep(1)  # Let motor break

    # Drive down vertical axis
    brick_pi.set_motor_position_relative(MOTOR_VERTICAL_AXIS, -1020)
    time.sleep(4)  # Let motor run

    # Drive down horizontal axis
    brick_pi.set_motor_position_relative(MOTOR_HORIZONTAL_AXIS, 520)
    time.sleep(2)  # Let motor run

    # Close gripper
    brick_pi.set_motor_position_relative(MOTOR_GRIPPER, -12000)
    time.sleep(10)  # Let motor run

    # Drive up horizontal axis
    brick_pi.set_motor_position_relative(MOTOR_HORIZONTAL_AXIS, -520)
    time.sleep(2)  # Let motor run

    # Reset vertical axis
    while read_sensor(SENSOR_VERTICAL_AXIS) == 0:
        brick_pi.set_motor_power(MOTOR_VERTICAL_AXIS, 30)
        time.sleep(0.02)  # Reduce CPU load
    brick_pi.set_motor_power(MOTOR_VERTICAL_AXIS, 0)
    time.sleep(1)  # Let motor break

    # Start truck and wait for space
    mqtt_client.publish(MQTT_TOPIC_PUBLISH, MQTT_MESSAGE_PUBLISH, 1)
    time.sleep(2)  # Let truck drive

    # Turn rotation axis
    brick_pi.set_motor_position_relative(MOTOR_ROTATION_AXIS, -3140)
    time.sleep(5)  # Let motor run

    # Drive down horizontal axis
    brick_pi.set_motor_position_relative(MOTOR_HORIZONTAL_AXIS, 1560)

    # Drive down vertical axis
    brick_pi.set_motor_position_relative(MOTOR_VERTICAL_AXIS, -700)
    time.sleep(5)  # Let motor run

    # Open gripper
    brick_pi.set_motor_position_relative(MOTOR_GRIPPER, 12000)
    time.sleep(8)  # Let motor run

    # Reset vertical axis
    while read_sensor(SENSOR_VERTICAL_AXIS) == 0:
        brick_pi.set_motor_power(MOTOR_VERTICAL_AXIS, 30)
        time.sleep(0.02)  # Reduce CPU load
    brick_pi.set_motor_power(MOTOR_VERTICAL_AXIS, 0)
    time.sleep(1)  # Let motor break

    # Reset horizontal axis
    while read_sensor(SENSOR_HORIZONTAL_AXIS) == 0:
        brick_pi.set_motor_power(MOTOR_HORIZONTAL_AXIS, -80)
        time.sleep(0.02)  # Reduce CPU load
    brick_pi.set_motor_power(MOTOR_HORIZONTAL_AXIS, 0)
    time.sleep(1)  # Let motor break

    # Drive down horizontal axis
    brick_pi.set_motor_position_relative(MOTOR_HORIZONTAL_AXIS, 750)
    time.sleep(2)  # Let motor break

    print("Unloading of truck finished")
    currently_running = False


# Protection to avoid running multiple times
currently_running = True