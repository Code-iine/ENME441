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


Shifter = Shifter(serialPin,latchPin,clockPin)
Bug = Bug()
speed = Bug.timestep #Original speed

def flipBug():
    Bug.flip_state()


#GPIO.add_event_detect(15, GPIO.BOTH, callback = flipBug, bouncetime = 100)
GPIO.add_event_detect(15, GPIO.BOTH, callback = lambda channel: flipBug, bouncetime = 100)

try:
    while True:
        if GPIO.input(14) == 1:
            Bug.switch_on()
            Bug.start()
            print(GPIO.input(15))
        else:
            Bug.switch_off()
            Bug.stop()
        
        if GPIO.input(18) == 1:
            #print("fast")
            Bug.timestep = Bug.timestep / 3
        else:
            #print("Regular")
            Bug.timestep = speed
        time.sleep(0.01)

except KeyboardInterrupt: # stop gracefully on ctrl-C
    print('\nExiting')

finally: #Turn off all pins
   Bug.stop()
   #Shifter.shiftByte(0)
   GPIO.cleanup()
