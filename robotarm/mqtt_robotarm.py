import time
import crane
from crane import brick_pi
import paho.mqtt.client as client
import notifier

# setup robotarm
mqttnotifier = notifier.Notifier()
crane.initialize()
crane.calibration()


def onMessage(client, userdata, msg):
    print("Message Topic: " + msg.topic + " Payload: " + msg.payload.decode('UTF-8'))
    if msg.topic == "/robotarm/queque":
        crane.moveARMup()
        mqttnotifier.notifyStatusRobotarm()
    elif msg.topic == "/robotarm/input":
        crane.moveARMdown()
        crane.run_load()
        #crane.pickupPallet()
        print("picking up pallet")
        time.sleep(5)
        crane.run_unload()
        #crane.putdownPallet()
        print("putting down pallet")
        crane.moveARMup()
        mqttnotifier.notify_SwarmRobot_unloaded()

    elif msg.topic == "/robotarm/status_out":
        crane.moveARMdown()
        pass


def onConnect(client, userdata, flags, rc):
    client.subscribe("/robotarm/queque")
    client.subscribe("/robotarm/input")
    client.subscribe("/robotarm/status_out")


hostname = "192.168.188.28"
port = 1883
connection_alive = 60

client = client.Client()
client.on_connect = onConnect
client.on_message = onMessage
client.connect(hostname, port)
client.loop_forever()
