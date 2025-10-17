from shifter import Shifter
import time
import RPi.GPIO as GPIO

serialPin = 23
latchPin = 24
clockPin = 25

Shifter1 = Shifter(serialPin,latchPin,clockPin)

try:
  print("testing")
  while 1:
    for i in range(108):
        Shifter1.shiftByte(i)
        time.sleep(0.5)
except:
  GPIO.cleanup()

finally: #Turn off all pins
   Shifter1.shiftByte(0)
   GPIO.cleanup()