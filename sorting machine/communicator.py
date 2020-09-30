from machine import *
from pallet import *
from ramp import *
from enum import Enum 
import csv 
import time                                                                # import the time library for the sleep function
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import signal
import sys

class State(Enum):
    busy = 1
    free = 2
   
class Communicator:

    machine = None
    ramps = []
    swarmRobotStates = []

    def signal_handler(self, sig, frame):                                  # Interrupt handler. Handles user interrupting the machine by pressing Cntr + C
        self.machine.shutDown()
        print('Machine turned off. Pusher is released.')
        sys.exit(0)

    def __init__(self):
        
        signal.signal(signal.SIGINT, self.signal_handler)                  # Setting up the program stop handler

        self.state = State.busy                                            # Communicator state set to "busy" while the machine is calibrating
        self.machine = Machine(self)                                       # Initializing the machine + calibration of the pushers and band
        self.machine.calibrate()

        self.state = State.free                                            # Machine is calibrated and communicator state is set to "free"
        publish.single("sorting-machine/state", "free", hostname = hostname)
        
        for i in range(1, 7):                                              # Initialization of the six ramps
            ramp = Ramp(i)
            self.ramps.append(ramp)
        
        for i in range(0,10):                                               # Initializing a list with states of each of the ten swarm robots. At the beginning the state is set to unknown. When the machine receives an update from the swarm robots via MQTT, the states are going to be updated
            self.swarmRobotStates.append('Unknown')

    def generatePallet(self, message):                                     # Method for generating of a pallet object out of the MQTT message payload
        message_infos = message.split() 
        pallet_id = message_infos[1]
        pallet = Pallet(pallet_id)
        print("PalletID:" + str(pallet_id))
        return pallet
        
    def setRobotStatus(self,robotId, message):                             # Updating the status of a swarm robot

        self.swarmRobotStates[robotId] = message
    
        

    def checkForFullRamps(self, ramp_id):                                  # 
        
        self.sendPickupMessage(ramp_id)

    def sendPickupMessage(self,ramp_id):                                   # Method for informing a swarm robot, when a pallet has been sorted and is ready for pickup
        ramp = self.ramps[ramp_id]
        pallet = ramp.pallets[0]
        freeRobot = self.findFreeRobot()
        palletDestination = ''
       
        with open('signatures.csv') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',' )
            for row in readCSV:
                if row[0] == str(pallet.pallet_signature):
                    palletDestination = row[3]
        
        publish.single(freeRobot + "/order", "Bring Pallet-ID " + pallet.pallet_id + " From #SortingRamp" + str(ramp_id) + " To #" + palletDestination, hostname = hostname) # !---- Uncomment line for using MQTT ----!
        print("message sent: " +freeRobot + "/order", "Bring Pallet-ID " + pallet.pallet_id + " From #SortingRamp" + str(ramp_id) + " To #" + palletDestination)

    def finalizePickUp(self, message):                                  # Method for cleaning the pallet data from the platform, when it has been picked by a swarm robot
        message_infos = message.split() 
        pallet_id = message_infos[1]
        
        for ramp in self.ramps:
            for pallet in ramp.pallets:
                if pallet_id == pallet.pallet_id:
                    ramp.pallets.remove(pallet)
                    print("Pallet " + pallet_id + " has been picked up" )
        

        self.state= State.free
        publish.single("sorting-machine/state", "free", hostname=hostname) 

    def findFreeRobot(self):                                            # Method for finding a free robot, which could pick up the pallet
        robotaddress = ''

        print('searching for free swarm robots...')

        while robotaddress == '':
            for i in range(0,10):
                
                if self.swarmRobotStates[i] == 'Parking':               # the sorting machine check for a free robot by searching for state "parking" in the list of list of swarm robots states
                    robotId = i + 1
                    if robotId < 10: 
                        robotaddress = 'swarm-robot0' + str(robotId)
                    else: robotaddress = 'swarm-robot' + str(robotId)
                    print('Free swarm robot found: swarm-robot' + str(robotId))
                    break
            time.sleep(3)
        return robotaddress

    def getNotified(self,pallet):                                       # Method for informing the communicator, when the machine has a pallet sorted
        print('Pallet with ID' + pallet.pallet_id + ' identified as ' + str(pallet.pallet_content) + ' has been sorted onto ramp ' + str(pallet.pallet_signature))
        
        if pallet.pallet_signature == 1:
            self.ramps[0].pallets.append(pallet)
        if pallet.pallet_signature == 2:
            self.ramps[1].pallets.append(pallet)
        if pallet.pallet_signature == 3:
            self.ramps[2].pallets.append(pallet)
        if pallet.pallet_signature == 4:
            self.ramps[3].pallets.append(pallet)
        if pallet.pallet_signature == 5:
            self.ramps[4].pallets.append(pallet)
        if pallet.pallet_signature == 6:
            self.ramps[5].pallets.append(pallet)
        
        
        self.checkForFullRamps(pallet.pallet_signature-1)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() - if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("sorting-machine/order")
    client.subscribe("sorting-machine/pickup")

    client.subscribe("swarm-robot01/status")
    client.subscribe("swarm-robot02/status")
    client.subscribe("swarm-robot03/status")
    client.subscribe("swarm-robot04/status")
    client.subscribe("swarm-robot05/status")
    client.subscribe("swarm-robot06/status")
    client.subscribe("swarm-robot07/status")
    client.subscribe("swarm-robot08/status")
    client.subscribe("swarm-robot09/status")
    client.subscribe("swarm-robot10/status")
 
# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    
    if msg.topic == "sorting-machine/order":                                # Ordering of Sorting
        print("message received: " + msg.topic+" "+str(msg.payload))

        if communicator.state == State.free:                                # Sorting only if the state is "free" 
            communicator.state = State.busy                                 # Setting state to "busy" before the sorting process is started
            publish.single("sorting-machine/state", "busy", hostname=hostname)
            pallet = communicator.generatePallet(msg.payload)
            print('sorting started...')
            communicator.machine.sort(pallet)
            print('sorting complete!')

    if msg.topic == "sorting-machine/pickup":                               #"Pallet picked up by swarm robot X" message received
        print("message received: " + msg.topic+" "+str(msg.payload))

        communicator.finalizePickUp(msg.payload)


    if msg.topic == "swarm-robot01/status":                                 # Swarm Robots topics, sharing the swarm robot status with the sorting machine.
        communicator.setRobotStatus(0,msg.payload) 
        print("message received: " + msg.topic+" "+str(msg.payload))
    if msg.topic == "swarm-robot02/status":    
        communicator.setRobotStatus(1,msg.payload) 
        print("message received: " + msg.topic+" "+str(msg.payload))
    if msg.topic == "swarm-robot03/status":    
        communicator.setRobotStatus(2,msg.payload) 
        print("message received: " + msg.topic+" "+str(msg.payload))
    if msg.topic == "swarm-robot04/status":  
        communicator.setRobotStatus(3,msg.payload)  
        print("message received: " + msg.topic+" "+str(msg.payload))
    if msg.topic == "swarm-robot05/status":   
        communicator.setRobotStatus(4,msg.payload)  
        print("message received: " + msg.topic+" "+str(msg.payload))
    if msg.topic == "swarm-robot06/status":   
        communicator.setRobotStatus(5,msg.payload)  
        print("message received: " + msg.topic+" "+str(msg.payload))
    if msg.topic == "swarm-robot07/status":   
        communicator.setRobotStatus(6,msg.payload) 
        print("message received: " + msg.topic+" "+str(msg.payload)) 
    if msg.topic == "swarm-robot08/status":    
        communicator.setRobotStatus(7,msg.payload) 
        print("message received: " + msg.topic+" "+str(msg.payload))
    if msg.topic == "swarm-robot09/status":   
        communicator.setRobotStatus(8,msg.payload) 
        print("message received: " + msg.topic+" "+str(msg.payload)) 
    if msg.topic == "swarm-robot10/status":                                    
        communicator.setRobotStatus(9,msg.payload)  

# Create an MQTT client and attach our routines to it.

client = mqtt.Client()                             
client.on_connect = on_connect                     
client.on_message = on_message                     

hostname = "test.mosquitto.org"
port = 1883
connection_alive = 60

client.connect(hostname, port, connection_alive)                 

communicator = Communicator()

# Process network traffic and dispatch callbacks. This will also handle
# reconnecting. Check the documentation at
# https://github.com/eclipse/paho.mqtt.python
# for information on how to use other loop*() functions
client.loop_forever()                              


