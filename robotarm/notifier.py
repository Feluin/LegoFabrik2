import paho.mqtt.publish as publish

hostname="192.168.188.28"
class Notifier:



    def __init__(self):
        pass

    def notifyStatusRobotarm(self):
        publish.single(topic="/robotarm/status",payload= "Free",hostname=hostname)

    def notify_SwarmRobot_unloaded(self):
        publish.single(topic="/robotarm/unload",payload="Pallet ready to be picked up",hostname=hostname)
