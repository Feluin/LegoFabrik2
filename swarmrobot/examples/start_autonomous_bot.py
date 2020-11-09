import logging

from botlib.autonomousBot import SwarmLabBot


def main():
    with SwarmLabBot() as bot:
        bot.start()

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    main()
