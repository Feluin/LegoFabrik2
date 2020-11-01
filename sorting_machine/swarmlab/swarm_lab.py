import logging
import time

import machine


def main():
    sorter = machine.Machine()
    print ("test")
    sorter.calibrate()
    time.sleep(3)
    sorter.sort_random()



if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    main()