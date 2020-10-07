import logging
import time

from botlib.autonomousBot import AutonomousBot
import cv2

def main():
    #cv2.VideoCapture(0)
    with AutonomousBot() as bot:
        time.sleep(1)
        bot.start_detection_thread(bot.start_sonar_detection)
        time.sleep(5)
        bot.anlignobstacle()

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    main()

