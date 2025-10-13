from shifter import Shifter
import time
import RPi.GPIO as GPIO

serialPin = 23
latchPin = 24
clockPin = 25


try:
  Shifter = Shifter(serialPin,latchPin,clockPin)
  print("testing")
  while 1:
    for i in range(2**8):
        Shifter.shiftByte(i)
        time.sleep(0.5)
except:
  GPIO.cleanup()