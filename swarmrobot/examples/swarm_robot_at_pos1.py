import time

import examples.swarmlab_with_Mqtt as swarmrobot
#swarmrobot.bot.move_toRobotarm()
#swarmrobot.client.subscribe("/robotarm/status")
#swarmrobot.mqttnotifier.alert_robotarm()
swarmrobot.startingpos = 1
swarmrobot.mqttnotifier.simulate_Order()
swarmrobot.client.loop_forever()