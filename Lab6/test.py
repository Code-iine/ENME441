import RPi.GPIO as GPIO
import time

# Set the GPIO numbering scheme to BCM
GPIO.setmode(GPIO.BCM)

class Shifter:
    """
    A class to handle the functionality of a 74HC595 shift register.
    """

    def __init__(self, serialPin, clockPin, latchPin):
        """
        Initializes the Shifter object.
        
        :param serialPin: The GPIO pin number for serial data input (DS).
        :param clockPin: The GPIO pin number for the shift register clock (SHCP).
        :param latchPin: The GPIO pin number for the storage register clock (STCP).
        """
        # Assign pin numbers to class attributes
        self.serialPin = serialPin
        self.clockPin = clockPin
        self.latchPin = latchPin

        # Setup the GPIO pins as outputs, with latch and clock starting low
        GPIO.setup(self.serialPin, GPIO.OUT)
        GPIO.setup(self.latchPin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.clockPin, GPIO.OUT, initial=GPIO.LOW)

    def __ping(self, pin):
        """
        Private method to pulse a GPIO pin HIGH and then LOW.
        This is a convention for "private" methods in Python.
        
        :param pin: The pin number to pulse.
        """
        GPIO.output(pin, GPIO.HIGH)
        # The time.sleep(0) is negligible but can help ensure the pulse is registered
        time.sleep(0) 
        GPIO.output(pin, GPIO.LOW)

    def shiftByte(self, byteValue):
        """
        Public method to send an 8-bit value to the shift register.
        
        :param byteValue: An integer (0-255) to be shifted out.
        """
        # Iterate through each bit of the byte, from LSB to MSB
        for i in range(8):
            # Set the serial pin HIGH or LOW based on the current bit
            # The expression (byteValue & (1 << i)) will be non-zero (True) if the bit is 1
            GPIO.output(self.serialPin, byteValue & (1 << i))
            
            # Pulse the clock pin to shift the bit into the register
            self.__ping(self.clockPin)
        
        # Pulse the latch pin to move the data from the shift register to the output pins
        self.__ping(self.latchPin)


# --- Main program ---

# Define GPIO pins to be used for the shift register
DATA_PIN = 23
LATCH_PIN = 24
CLOCK_PIN = 25

try:
    # Instantiate the Shifter class with the defined pins
    my_shifter = Shifter(serialPin=DATA_PIN, clockPin=CLOCK_PIN, latchPin=LATCH_PIN)
    
    print("Starting the LED counter loop. Press CTRL+C to exit.")
    
    # Main loop to cycle through all possible 8-bit values
    while True:
        # Count from 0 to 255 (2**8 - 1)
        for i in range(2**8):
            # Call the public method of our shifter instance
            my_shifter.shiftByte(i)
            time.sleep(0.1) # Slowed down slightly for better visualization

except KeyboardInterrupt:
    print("\nProgram terminated by user.")

finally:
    # This will be executed on exit, ensuring the GPIO pins are reset
    print("Cleaning up GPIO pins.")
    GPIO.cleanup()