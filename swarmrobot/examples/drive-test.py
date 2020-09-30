import time

from botlib.motor import Motor

if __name__ == '__main__':
    Motor._bp.set_motor_power(Motor._bp.PORT_C, 20)
    time.sleep(1)
    Motor._bp.set_motor_power(Motor._bp.PORT_C, 0)
    time.sleep(1)
    Motor._bp.set_motor_power(Motor._bp.PORT_C, -20)
    time.sleep(1)
    Motor._bp.set_motor_power(Motor._bp.PORT_C, 0)
