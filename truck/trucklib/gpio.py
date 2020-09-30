""" This file contains a class used for controlling the GPIO. """

# Import system libraries
import time
import threading

# Import Raspberry Pi library
import RPi.GPIO as gpio


class GpioController:
    """ Helps to control the connected GPIO pins.
    `on_time` and `off_time` is in seconds. """

    def __init__(self, backlight_pin_number, on_time, off_time):
        self.backlight_pin_number = backlight_pin_number
        self.should_blink = False
        self.on_time = on_time
        self.off_time = off_time
        gpio.setmode(gpio.BCM)  # Set pinmap numbering scheme
        gpio.setup(self.backlight_pin_number, gpio.OUT)
        threading.Thread(target=self.__blink).start()  # Start blink thread

    def __blink(self):
        """ This private function should be called as a thread. """

        while True:
            if self.should_blink:
                gpio.output(self.backlight_pin_number, gpio.HIGH)
                time.sleep(self.on_time)
                gpio.output(self.backlight_pin_number, gpio.LOW)
                time.sleep(self.off_time)
            else:
                time.sleep(0.5)  # Reduce CPU load

    def set_backlight(self, should_be_turned_on):
        """ This function sets the output of the backlight according
        to `should_be_turned_on`. """

        self.should_blink = True if should_be_turned_on else False
