import logging

from botlib.autonomousBot import AutonomousBot


def main():
    with AutonomousBot() as bot:
        bot.start()


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    main()
