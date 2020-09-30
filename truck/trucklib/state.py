""" This file is for handling the state of the truck
and thus the whole system. """


class StateController:
    """ Responsible for storing and changing the state of the truck. """

    def __init__(self, mqtt_controller, gpio_controller,
                 mqtt_topic,
                 motor_controller,
                 motor_target_power,
                 initial_state="DRIVING_WITH_PALLET"):
        self.mqtt_controller = mqtt_controller
        self.mqtt_controller.own_state_controller = self
        self.mqtt_topic = mqtt_topic
        self.gpio_controller = gpio_controller
        self.motor_controller = motor_controller
        self.motor_target_power = motor_target_power
        self.current_state = initial_state

    def set_state(self, new_state):
        """ For changing the current_state!
        Always use this function instead of direct
        access to `current_state`. """

        if new_state == self.current_state:
            return  # No change in state necessary

        if (new_state != "DRIVING_WITH_PALLET" and
                new_state != "DRIVING_WITHOUT_PALLET" and
                new_state != "WAITING_FOR_LOADING" and
                new_state != "WAITING_FOR_UNLOADING"):
            raise Exception("Unknown state: " + new_state)

        print("Changing state to: " + new_state)

        if (new_state == "DRIVING_WITH_PALLET" or
                new_state == "DRIVING_WITHOUT_PALLET"):
            self.motor_controller.target_power = self.motor_target_power
            self.gpio_controller.set_backlight(False)

        elif (new_state == "WAITING_FOR_LOADING" or
              new_state == "WAITING_FOR_UNLOADING"):
            self.motor_controller.target_power = 0
            self.gpio_controller.set_backlight(True)

        self.mqtt_controller.publish(self.mqtt_topic, new_state, 1)
        self.current_state = new_state

    def get_state(self):
        """ This is a getter for the class variable `current_state`.
        Always use this getter if possible. """

        return self.current_state

    def is_waiting(self):
        """ This function returns true if the truck is not moving. """

        return (self.current_state == "WAITING_FOR_LOADING" or
                self.current_state == "WAITING_FOR_UNLOADING")
