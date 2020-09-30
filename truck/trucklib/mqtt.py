""" This file contains a class for mqtt connection. """

import paho.mqtt.client as mqtt


class MqttController(mqtt.Client):
    """ This class is for interaction with the mqtt procotol.
    We are here extending the paho mqtt client class. """

    def on_connect(self, mqttc, obj, flags, rc):
        """ Callback for mqtt client on successful connection. """

        print('Successfully connected to broker with result code: ' + str(rc))
        # Only subscribe to topic if connection established
        self.subscribe(self.own_topic, qos=1)
        self.subscribe(self.own_topic_emergency, qos=1)

    def on_message(self, mqttc, obj, msg):
        """ Callback for mqtt client on new message received. """

        print('Received mqtt message: ' + str(msg.payload))
        if msg.topic == self.own_topic_emergency:
            self.own_callback_emergency()

        # Call passed callback from constructor
        self.own_callback(self.own_state_controller)

    def init(self, broker_address, topic, topic_emergency,
             callback, callback_emergency):
        self.connect(broker_address)
        self.own_topic = topic
        self.own_topic_emergency = topic_emergency
        self.own_callback = callback
        self.own_callback_emergency = callback_emergency
        # `state_controller` must be set by state_controller manually
        self.own_state_controller = None
        return self
