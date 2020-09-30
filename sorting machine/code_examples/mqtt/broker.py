# MQTT Publish Demo
# Publish two messages, to two different topics

import paho.mqtt.publish as publish

publish.single("sorting-machine/test", "Hello", hostname="test.mosquitto.org")
publish.single("sorting-machine/test", "World!", hostname="test.mosquitto.org")
print("Done")