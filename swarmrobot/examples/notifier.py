import paho.mqtt.publish as publish

hostname="192.168.188.28"
class Notifier:



    def __init__(self):
        pass

    def simulate_Order(self):

        publish.single(topic="/warehouse/order", payload="1", hostname=hostname)


    def alert_sorting_machine(self):
        publish.single(topic="/sorting_machine/queque", payload="Pallet incoming", hostname=hostname)

    def notifiy_sorting_Machine_unloaded(self):
        publish.single(topic="/sorting_machine/receiving_department",payload="Pallet unloaded",hostname=hostname)

    def notifiy_sorting_Machine_picked_up(self):
        publish.single(topic="/sorting_machine/status_out", payload="Pallet picked up", hostname=hostname)

    def alert_robotarm(self):
        publish.single(topic="/robotarm/queque", payload="Pallet incoming", hostname=hostname)

    def notifiy_robotarm_unloaded(self):
        publish.single(topic="/robotarm/input", payload="Pallet delivered", hostname=hostname)

    def notifiy_robotarm_picked_up(self):
        publish.single(topic="/robotarm/status_out", payload="Pallet picked up", hostname=hostname)

    def notifiy_warehouse_incoming(self):
        publish.single(topic="/warehouse/status", payload="Free", hostname=hostname)

    def notifiy_warehouse_delivered(self):
        pass

    def alert_next_robot(self):
        publish.single(topic="/warehouse/order", payload="2", hostname=hostname)