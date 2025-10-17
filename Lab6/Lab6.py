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
    for i in range(2**8):
        Shifter1.shiftByte(i)
        time.sleep(0.5)
except:
  GPIO.cleanup()

finally:
   Shifter1.shiftByte(0)
   GPIO.cleanup()