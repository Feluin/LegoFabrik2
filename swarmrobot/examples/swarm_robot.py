import logging
import time

from botlib.autonomousBot import SwarmLabBot


def main():
    # cv2.VideoCapture(0)
    with SwarmLabBot() as bot:
        bot._drive_motor.change_power(0)
        bot.steer(-0.8)
        time.sleep(1)
        bot.steer(0)
        time.sleep(1)
        bot._drive_motor.change_power(25)
        time.sleep(5)
        bot._drive_motor.change_power(0)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    main()
