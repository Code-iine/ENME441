from RPi import GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)

class Shifter:
    _instances = []  # Track all shifters for synchronized output

    def __init__(self, data, clock, latch):
        self.dataPin = data
        self.latchPin = latch
        self.clockPin = clock
        GPIO.setup(self.dataPin, GPIO.OUT)
        GPIO.setup(self.latchPin, GPIO.OUT)
        GPIO.setup(self.clockPin, GPIO.OUT)
        self.state = 0  # current 8-bit output state
        Shifter._instances.append(self)

    def ping(self, p):  # ping the clock or latch pin
        GPIO.output(p, 1)
        sleep(0)
        GPIO.output(p, 0)

    def _write_bits(self):
        """Push current states of all shifters simultaneously."""
        # Combine all shifter states into one concatenated word
        combined = 0
        total_bits = 0
        for sh in reversed(Shifter._instances):  # maintain chain order
            combined <<= 8
            combined |= sh.state
            total_bits += 8

        # Shift the combined word once
        first = Shifter._instances[0]
        for i in range(total_bits):
            bit = (combined >> (total_bits - 1 - i)) & 1
            GPIO.output(first.dataPin, bit)
            first.ping(first.clockPin)
        first.ping(first.latchPin)

    def shiftWord(self, dataword, num_bits):
        """Set state and update outputs in sync with other instances."""
        self.state = dataword & ((1 << num_bits) - 1)
        self._write_bits()

    def shiftByte(self, databyte):
        self.shiftWord(databyte, 8)
