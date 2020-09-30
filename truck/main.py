""" This file is an example how to use the trucklib.
It is also used for shooting the video. """

# Import system libraries
import sys

# Import custom libraries
from trucklib import motor
from trucklib import brickpi3
from trucklib import vision
from trucklib import streaming
from trucklib import mqtt
from trucklib import state
from trucklib import gpio

# Import third-party libraries
from simple_pid import PID

TARGET_POWER = 30
VIDEO_FRAMERATE = 15
VIDEO_SERVER = 'tcp://192.168.1.123:5555'
MQTT_BROKER = '192.168.1.123'
MQTT_TOPIC_SUBSCRIBE = 'robot'
MQTT_TOPIC_PUBLISH = 'truck'
MQTT_TOPIC_EMERGENCY = 'emergency'
BATTERY_CUT_OFF_VOLTAGE = 10
BACKLIGHT_LED_PIN = 17  # Raspberry Pi BCM GPIO 17


def mqtt_callback(state_controller):
    """ Called after receiving a message on the MQTT_TOPIC_SUBSCRIBE. """

    if state_controller.get_state() == "WAITING_FOR_LOADING":
        state_controller.set_state("DRIVING_WITH_PALLET")
    else:
        state_controller.set_state("DRIVING_WITHOUT_PALLET")


def mqtt_emergency():
    """ Called after receiving a message on the MQTT_TOPIC_EMERGENCY. """

    brick_pi.reset_all()
    vc.camera.release()
    sys.exit()


brick_pi = brickpi3.BrickPi3()
mc = motor.MotorController(brick_pi, brick_pi.PORT_B, brick_pi.PORT_C)
vc = vision.VisionController(VIDEO_FRAMERATE)
sc = streaming.StreamingController()
mqttc = mqtt.MqttController().init(MQTT_BROKER,
                                   MQTT_TOPIC_SUBSCRIBE,
                                   MQTT_TOPIC_EMERGENCY,
                                   mqtt_callback,
                                   mqtt_emergency)
gc = gpio.GpioController(BACKLIGHT_LED_PIN, 1, 1)  # 1s On-Off-Time
stc = state.StateController(mqttc, gc, MQTT_TOPIC_PUBLISH, mc, TARGET_POWER)
pid = PID(-0.68, 0, -0.05, setpoint=0)  # P = -0.68 and D = -0.05
pid.sample_time = 0.07  # Adapted to the video framerate
pid.output_limits = (-1, 1)


if __name__ == "__main__":
    try:
        # This uses a server on a different pc to send the stream to
        # If no server software is available, comment out all sc...
        sc.connect(VIDEO_SERVER)

        mc.target_power = TARGET_POWER
        if TARGET_POWER > 0:
            mc.steering_calibration()

        mqttc.loop_start()

        # The while-loop should be as fast as possible without delays!
        while True:
            mc.loop()

            if vc.ready():
                _, line_image, current_position, stop = vc.loop()
                if stop:  # if stop-sign detected
                    if stc.get_state() == "DRIVING_WITH_PALLET":
                        stc.set_state("WAITING_FOR_UNLOADING")
                    elif stc.get_state() == "DRIVING_WITHOUT_PALLET":
                        stc.set_state("WAITING_FOR_LOADING")

                sc.loop(line_image)
                if not stc.is_waiting():
                    mc.steer(pid(current_position))  # using the pid controller

            # Battery protection
            if brick_pi.get_voltage_battery() < BATTERY_CUT_OFF_VOLTAGE:
                raise Exception('Battery voltage too low: ' +
                                str(brick_pi.get_voltage_battery()))

    finally:
        brick_pi.reset_all()
        mqttc.disconnect()
        vc.camera.release()
