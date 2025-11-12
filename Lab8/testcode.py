# Shift register class (Edited for simultaneous operation)

from RPi import GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)

class Shifter():

    def __init__(self, data, clock, latch, num_bits=8):
        """
        Initialize the Shifter.
        
        - data, clock, latch: The BCM pin numbers.
        - num_bits: The total number of bits in your shift register chain
                    (e.g., 16 for two 8-bit registers).
        """
        self.dataPin = data
        self.latchPin = latch
        self.clockPin = clock
        self.num_bits = num_bits
        
        # This is the new internal state variable.
        # It holds the state of all bits in the chain.
        self.state = 0

        GPIO.setup(self.dataPin, GPIO.OUT)
        GPIO.setup(self.latchPin, GPIO.OUT)
        GPIO.setup(self.clockPin, GPIO.OUT)
        
        self.update() # Initialize registers to all-low

    def ping(self, p):  # ping the clock or latch pin
        GPIO.output(p, 1)
        sleep(0) # This pause is extremely short, almost zero.
        GPIO.output(p, 0)

    # NEW METHOD: set_bits
    # This is what your motor's __step() method should call.
    # It updates the internal state *without* sending to hardware.
    def set_bits(self, mask, value):
        """
        Updates a portion of the internal state. This does NOT
        send the data to the hardware yet.
        
        - mask: An integer with 1s for the bits this call "owns".
                (e.g., 0b00001111 for motor 1)
        - value: The new value for those bits (e.g., 0b00001010)
        """
        # Clear the bits defined by the mask
        self.state &= ~mask
        # Set the new bits from the value, ensuring we only use the mask
        self.state |= (value & mask)

    # NEW METHOD: update
    # This is what your main loop should call once per cycle.
    # It sends the *entire* combined state to the hardware.
    def update(self):
        """
        Shifts the *entire* current 'self.state' out to the
        shift registers and latches it.
        """
        # We shift LSB-first, matching the original code's logic
        for i in range(self.num_bits):
            # Check the i-th bit of self.state and set the data pin
            GPIO.output(self.dataPin, self.state & (1 << i))
            self.ping(self.clockPin)
        
        # Once all bits are shifted, latch them to the outputs
        self.ping(self.latchPin)

    #
    # The original 'shiftWord' and 'shiftByte' methods
    # have been removed as they are incompatible with
    # simultaneous, stateful control.
    #

# ---
# Example of how to use the new class:
# ---
# (This is a conceptual example, not part of the class)
#
# # Assume a 16-bit chain for two 4-bit motors (or one 8-bit)
# s = Shifter(data=16, clock=20, latch=21, num_bits=16)
#
# # Motor 1 (m1) controls the first 4 bits (LSBs)
# m1_mask = 0b0000000000001111
# m1_step_pattern = 0b0000000000001010 # e.g., A-B coils high
#
# # Motor 2 (m2) controls the next 4 bits
# m2_mask = 0b0000000011110000
# m2_step_pattern = 0b0000000001010000 # e.g., B-C coils high
#
# # In your __step() methods (or main loop):
# # m1.__step() would call:
# s.set_bits(m1_mask, m1_step_pattern)
#
# # m2.__step() would call:
# s.set_bits(m2_mask, m2_step_pattern)
#
# # At the end of your main loop (after all motors have "stepped"):
# s.update()
#
# # This s.update() call sends the combined state (0b0000000001011010)
# # to the hardware *at the same time*, moving both motors.
# ---

# (Original GPIO cleanup example - useful)
# try:
#     # ... your main loop ...
#     pass
# except KeyboardInterrupt:
#     GPIO.cleanup()