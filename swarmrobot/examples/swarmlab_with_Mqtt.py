import time

import paho.mqtt.client as client
import examples.notifier as notifier
from botlib.swarmlabbot import SwarmLabBot

# setup swarmrobot
bot = SwarmLabBot()
bot.setup()
mqttnotifier = notifier.Notifier()
startingpos = 1

"""Handle the POC simulation"""
def onMessage(client, userdata, msg):
    print("Message Topic: " + msg.topic + " Payload: " + msg.payload.decode('UTF-8'))
    if msg.topic == "/warehouse/order":
        if msg.payload.decode('UTF-8') == str(startingpos):
            client.unsubscribe("/warehouse/order")
            bot.moveToWarehouse(startingpos)
            # removefor infinite loop
            if (startingpos == 2):
                exit()
            bot.handleWarehouse()
            bot.moveToSortingFactory()
            client.subscribe("/sorting_machine/status")
            mqttnotifier.alert_sorting_machine()
    elif msg.topic == "/sorting_machine/status":
        client.unsubscribe("/sorting_machine/status")
        if msg.payload.decode('UTF-8') == "Free":
            bot.unload_sorting_Factory()
            mqttnotifier.notifiy_sorting_Machine_unloaded()
            client.subscribe("/sorting_machine/sorted")
    elif msg.topic == "/sorting_machine/sorted":
        if msg.payload.decode('UTF-8') == "OK":
            client.unsubscribe("/sorting_machine/sorted")
            bot.moveToSortingOutput()
            bot.pickup_Pallet_from_SortingMachine()
            mqttnotifier.notifiy_sorting_Machine_picked_up()
            client.subscribe("/robotarm/status")
            bot.move_toRobotarm()
            mqttnotifier.alert_robotarm()
            print("alerting robotarm")
    elif msg.topic == "/robotarm/status":
        client.unsubscribe("/robotarm/status")
        client.subscribe("/robotarm/unload")
        bot.unload_Robotarm()
        mqttnotifier.notifiy_robotarm_unloaded()
    elif msg.topic == "/robotarm/unload":
        client.unsubscribe("/robotarm/unload")
        bot.pickup_pallet_from_robotarm()
        mqttnotifier.notifiy_robotarm_picked_up()
        bot.moveFromArmAway()
        #uncomment if the warehouse ist implemented
        #client.subscribe("/warehouse/status")
        # time.sleep(1)
        #remove if warehouse is implemented
        #mqttnotifier.notifiy_warehouse_incoming()
        # elif msg.topic == "/warehouse/status":
        #    client.unsubscribe("/warehouse/status")
        bot.deliverPalletatwarehouse()
        mqttnotifier.notifiy_warehouse_delivered()
        bot.unload_at_warehouse()
        mqttnotifier.alert_next_robot()
        bot.move_to_Parkingspot()
        exit()

    else:
        pass

def onConnect(client, userdata, flags, rc):
    client.subscribe("/warehouse/order")


hostname = "192.168.188.28"
port = 1883
connection_alive = 60

client = client.Client()
client.on_connect = onConnect
client.on_message = onMessage
client.connect(hostname, port)
client.subscribe("/warehouse/order")