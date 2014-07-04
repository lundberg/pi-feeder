import RPi.GPIO as io
import logging
from time import sleep

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s')
log = logging.getLogger(__name__)


class Motor(object):

    FORWARD = 1
    BACKWARD = -1
    TOGGLE = 2

    def __init__(self, pins=None, use_pwm=False):
        # Configure pins
        io.setmode(io.BCM)
        self._pins = {
            'in_1': 17,
            'in_2': 4,
            'enable': 18,
        }
        self._pins.update(pins or {})

        # Setup pins for output
        for pin in self._pins.values():
            io.setup(pin, io.OUT)

        # Enable PWM, or not
        self._pwm = None
        self._speed = 100
        self._frequency = 300
        self.use_pwm = use_pwm

        # Initialize in pins as LOW
        map(self._low, ('in_1', 'in_2'))

        self._direction = None

    def _low(self, pin):
        io.output(self._pins[pin], io.LOW)

    def _high(self, pin):
        io.output(self._pins[pin], io.HIGH)

    def _get_direction(self):
        return self._direction

    def _set_direction(self, direction):
        """
        Set motor spin direction.

        :param direction:
        :return:
        """
        if not direction:
            log.debug('Set motor direction off')
            self.direction = None
            self._low('in_1')
            self._low('in_2')
        else:
            if self._direction and direction == Motor.TOGGLE:
                log.debug('Toggle motor direction')
                self._direction *= -1
            else:
                self._direction = direction

            if self._direction == Motor.FORWARD:
                log.debug('Set motor direction to forward')
                self._high('in_1')
                self._low('in_2')
            elif self._direction == Motor.BACKWARD:
                log.debug('Set motor direction to backward')
                self._low('in_1')
                self._high('in_2')

    def _get_use_pwm(self):
        return self._pwm is not None

    def _set_use_pwm(self, use):
        """
        Enable PWM to control motor speed and spin frequency.

        :param use:
        :return:
        """
        if use:
            self._pwm = io.PWM(self._pins['enable'], self._frequency)
        else:
            self._pwm = None

    def _get_speed(self):
        return self._speed

    def _set_speed(self, speed):
        """
        Set motor speed, if using PWM.

        :param speed:
        :return:
        """
        if self.use_pwm:
            log.debug('Set motor speed to %s', speed)
            self._speed = speed
            self._pwm.ChangeDutyCycle(self._speed)
        else:
            log.warning('Can not change motor speed to %s without using PWM!', speed)

    def _get_frequency(self):
        return self._frequency

    def _set_frequency(self, frequency):
        """
        Set motor spin frequency, if using PWM.

        :param frequency:
        :return:
        """
        if self.use_pwm:
            log.debug('Set motor PWM frequency to %s', frequency)
            self._frequency = frequency
            self._pwm.ChangeFrequency(self._frequency)
        else:
            log.warning('Can not change motor frequency to %s without using PWM!', frequency)

    direction = property(_get_direction, _set_direction)
    use_pwm = property(_get_use_pwm, _set_use_pwm)
    speed = property(_get_speed, _set_speed)
    frequency = property(_get_frequency, _set_frequency)

    def start(self, speed=None):
        """
        Start motor.
        Optional speed parameter, if using PWM.

        :param speed:
        :return:
        """
        if self.use_pwm:
            if speed is not None:
                self._speed = speed

            log.info('Start motor [speed=%s]', self._speed)
            self._pwm.start(self._speed)

        else:
            log.info('Start motor')
            self._high('enable')

        # Ensure motor direction
        if not self._direction:
            self.direction = Motor.FORWARD

    def stop(self):
        """
        Stop motor
        """
        log.info('Stop motor')
        if self.use_pwm:
            self._pwm.stop()
        else:
            self._low('enable')

    def forward(self):
        self.direction = Motor.FORWARD

    def backward(self):
        self.direction = Motor.BACKWARD

    def toggle(self):
        self.direction = Motor.TOGGLE


class Dispenser(object):

    def __init__(self):
        self.motor = Motor(use_pwm=True)
        self.motor.frequency = 1
        self.motor.speed = 85

    def feed(self, t=None, speed=None):
        self.motor.start(speed)
        if t:
            sleep(t)
            self.motor.stop()


if __name__ == '__main__':
    try:
        motor = Motor(use_pwm=False)

        motor.start()
        sleep(2)
        motor.toggle()
        sleep(2)
        motor.stop()

        # dispenser = Dispenser()
        # dispenser.feed(4)

    except (KeyboardInterrupt, Exception):
        print 'Abort'

    finally:
        io.cleanup()
