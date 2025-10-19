from shifter import Shifter
from shifter import Bug
import time
import RPi.GPIO as GPIO
import random

GPIO.setmode(GPIO.BCM)
range = [1, -1]

serialPin = 23
latchPin = 24
clockPin = 25

GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #S1
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #S2
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #s3



Bug = Bug()

try:
    while True:
        if GPIO.input(17):
            Bug.start()
        else:
            Bug.stop()

        time.sleep(0.01)

except KeyboardInterrupt: # stop gracefully on ctrl-C
    print('\nExiting')

finally: #Turn off all pins
   Bug.stop()
   #Shifter.shiftByte(0)
   GPIO.cleanup()
