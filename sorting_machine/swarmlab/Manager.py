import time

import paho.mqtt.client as client
import paho.mqtt.publish as publish
import machine
import machine
sorter= machine.Machine()
sorter.calibrate()

def onMessage(client, userdata, msg):
    print("message received: " + msg.topic + " " + str(msg.payload))
    if msg.topic=="/sorting_machine/queque":
        time.sleep(3)
        #handle multiple status
        client.publish("/sorting_machine/status","Free")
    elif msg.topic=="/sorting_machine/receiving_department":
        sortoutput=sorter.sort_random()
        client.publish("/sorting_machine/sorted", sortoutput)
        print(" send message /sorting_machine/sorted     "+sortoutput)
    else:
        print("unknown msg from"+msg.topic+" recieved")



def onConnect(client, userdata, flags, rc):
    client.subscribe("/sorting_machine/queque")
    client.subscribe("/sorting_machine/receiving_department")



hostname = "192.168.188.28"
port = 1883
connection_alive = 60

client = client.Client()
client.on_connect = onConnect
client.on_message = onMessage
client.connect(hostname, port)
client.loop_forever()