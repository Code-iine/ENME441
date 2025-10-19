from shifter import Shifter
import time
import RPi.GPIO as GPIO
import random

range = [1, -1]

serialPin = 23
latchPin = 24
clockPin = 25

Shifter1 = Shifter(serialPin,latchPin,clockPin)

try:
  print("testing")
  initial = 5
  while 1:

    step = random.choice(range)
    walk = initial + step

    if walk > 0 and walk < 8:
      initial = walk
    else:
      initial = 4

    Shifter1.shiftByte(1<<walk)
    time.sleep(0.05) #0.05 seconds

  

    '''
    for i in range(108):
        Shifter1.shiftByte(i)
        time.sleep(0.5)
        '''
except:
  GPIO.cleanup()

finally: #Turn off all pins
   Shifter1.shiftByte(0)
   GPIO.cleanup()