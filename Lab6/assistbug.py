# bug.py

import RPi.GPIO as GPIO
import time
import random

# --- GPIO Pin Definitions ---
# Shift Register Pins
DATA_PIN = 23
LATCH_PIN = 24
CLOCK_PIN = 25

# Input Switch Pins (using BCM numbering)
S1_PIN = 17  # On/Off switch
S2_PIN = 27  # Toggle Wrap switch
S3_PIN = 22  # Speed Boost switch

# Set GPIO mode and setup pins
GPIO.setmode(GPIO.BCM)
GPIO.setup([S1_PIN, S2_PIN, S3_PIN], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


# =================================================================
# CLASS DEFINITION for Shifter (unmodified)
# =================================================================
class Shifter:
    """A class to control a 74HC595 shift register."""
    def __init__(self, dataPin, latchPin, clockPin):
        self.dataPin, self.latchPin, self.clockPin = dataPin, latchPin, clockPin
        GPIO.setup(self.dataPin, GPIO.OUT)
        GPIO.setup(self.latchPin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.clockPin, GPIO.OUT, initial=GPIO.LOW)

    def __ping(self, pin):
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(0.00001) # A tiny delay is good practice
        GPIO.output(pin, GPIO.LOW)

    def shiftByte(self, byte_value):
        GPIO.output(self.latchPin, GPIO.LOW)
        for i in range(8):
            if (byte_value & (1 << i)):
                GPIO.output(self.dataPin, GPIO.HIGH)
            else:
                GPIO.output(self.dataPin, GPIO.LOW)
            self.__ping(self.clockPin)
        self.__ping(self.latchPin)


# =================================================================
# CLASS DEFINITION for Bug (modified for non-blocking updates)
# =================================================================
class Bug:
    """Encapsulates a randomly moving LED controlled by a shift register."""
    def __init__(self, timestep=0.1, x=3, isWrapOn=False):
        self.timestep = timestep
        self.x = x
        self.isWrapOn = isWrapOn
        self.__shifter = Shifter(DATA_PIN, LATCH_PIN, CLOCK_PIN)
        
        # Internal state attributes
        self._is_running = False
        self._last_update_time = 0

    def _update_position(self):
        """Calculates the bug's next position."""
        move = random.choice([-1, 1])
        if self.isWrapOn:
            self.x = (self.x + move) % 8
        else:
            new_position = self.x + move
            if 0 <= new_position <= 7:
                self.x = new_position

    def start(self):
        """Starts the bug's activity."""
        if self._is_running: return
        self._is_running = True
        self._last_update_time = time.time()
        print("Bug started.")
        # Light up the first LED immediately
        self.__shifter.shiftByte(1 << self.x)

    def stop(self):
        """Stops the bug's activity and turns off the LED."""
        if not self._is_running: return
        self._is_running = False
        print("Bug stopped.")
        self.__shifter.shiftByte(0)

    def update(self):
        """
        Main update method. Call this repeatedly in a loop.
        It handles timing and moves the bug one step if enough time has passed.
        """
        if not self._is_running:
            return

        current_time = time.time()
        if (current_time - self._last_update_time) >= self.timestep:
            self._update_position()
            self.__shifter.shiftByte(1 << self.x)
            self._last_update_time = current_time


# =================================================================
# MAIN PROGRAM LOGIC
# =================================================================
if __name__ == '__main__':
    print("Bug Control Program Initialized.")
    print("S1 (GPIO17): On/Off | S2 (GPIO27): Toggle Wrap | S3 (GPIO22): Speed Boost")
    print("Press Ctrl+C to exit.")

    # Instantiate Bug with default values
    bug = Bug()
    
    # Store the default speed to revert to
    DEFAULT_TIMESTEP = bug.timestep
    
    # Variables to track previous state for edge detection
    prev_s2_state = GPIO.input(S2_PIN)

    try:
        # Main infinite loop
        while True:
            # a. Read current state of all switches
            s1_state = GPIO.input(S1_PIN)
            s2_state = GPIO.input(S2_PIN)
            s3_state = GPIO.input(S3_PIN)

            # b. Control On/Off with S1
            if s1_state:
                bug.start()
            else:
                bug.stop()

            # c. Flip wrapping state when S2 changes from Off to On
            if s2_state and not prev_s2_state:
                bug.isWrapOn = not bug.isWrapOn
                print(f"Wrapping mode set to: {bug.isWrapOn}")
            prev_s2_state = s2_state # Update previous state for next loop

            # d. Increase speed when S3 is on
            if s3_state:
                bug.timestep = DEFAULT_TIMESTEP / 3.0
            else:
                bug.timestep = DEFAULT_TIMESTEP

            # CRITICAL: Call the bug's update method on every loop
            bug.update()

            # A small delay to prevent the loop from consuming 100% CPU
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    finally:
        # This code runs on exit to ensure everything is shut down cleanly
        bug.stop()
        GPIO.cleanup()
        print("GPIO cleaned up. Goodbye!")