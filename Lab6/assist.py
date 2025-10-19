# Lab6.py

from shifter import Shifter
import time
import RPi.GPIO as GPIO
import random

# Define the GPIO pins connected to the shift register
serialPin = 23
latchPin = 24
clockPin = 25


print("Starting random walk LED program...")
print("Press Ctrl+C to exit.")

# Instantiate the shifter object once before the main loop
# We place this in a 'finally' block to ensure cleanup happens
shifter_led = Shifter(serialPin,latchPin,clockPin)

try:
    # b. Start the LED in the middle of the display (position 4 out of 0-7)
    position = 4
    
    while True:
        # Calculate the byte to send. '1 << position' creates an integer
        # with only the bit at the current 'position' turned on.
        # e.g., position 4 -> 1 << 4 -> 16 -> 0b00010000
        byte_to_send = 1 << position
        
        # Send the byte to light up the single LED
        shifter_led.shiftByte(byte_to_send)
        
        # Wait for the specified time step
        time.sleep(0.05)
        
        # Randomly choose to move left (-1) or right (+1)
        move = random.choice([-1, 1])
        
        # Calculate the potential new position
        new_position = position + move
        
        # Prevent the LED from moving beyond the edges (0 or 7)
        # Only update the position if the new position is valid.
        if 0 <= new_position <= 7:
            position = new_position

except KeyboardInterrupt:
    # This block runs when you press Ctrl+C
    print("\nExiting program.")

finally:
    # This block runs no matter how the program exits, ensuring a clean shutdown
    print("Turning off LEDs and cleaning up GPIO.")
    shifter_led.shiftByte(0) # Turn all LEDs off
    GPIO.cleanup()