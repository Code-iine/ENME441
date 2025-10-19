import time
import RPi.GPIO as GPIO
import random
from shifter import Shifter
from shifter import Bug

GPIO.setmode(GPIO.BCM)
range = [1, -1]

serialPin = 23
latchPin = 24
clockPin = 25

GPIO.setup(14, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #S1
GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #S2
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #s3

GPIO.add_event_detect(15, GPIO.BOTH, callback=Bug.flip_state(), bouncetime = 100)



Bug = Bug()

try:
    while True:
        if GPIO.input(14) == 1:
            Bug.switch_on()
            Bug.start()
        else:
            Bug.switch_off()
            Bug.stop()
        
        if GPIO.input(18) == 1:
            Bug.timestep / 3
        else:
            Bug.timestep
        

        

        time.sleep(0.01)

except KeyboardInterrupt: # stop gracefully on ctrl-C
    print('\nExiting')

finally: #Turn off all pins
   Bug.stop()
   #Shifter.shiftByte(0)
   GPIO.cleanup()
