import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

class Shifter:
    def __init__(self,serialPin,latchPin,clockPin):
       self.serialPin = serialPin
       self.latchPin = latchPin
       self.clockPin = clockPin

       dataPin, latchPin, clockPin = 23, 24, 25

       GPIO.setup(dataPin, GPIO.OUT)
       GPIO.setup(latchPin, GPIO.OUT, initial=0)  # start latch & clock low
       GPIO.setup(clockPin, GPIO.OUT, initial=0)  
       
       pattern = 0b01100110        # 8-bit pattern to display on LED bar

    def __ping(self, p): #private method
        GPIO.output(p,1)
        time.sleep(0)
        GPIO.output(p,0)

    def shiftByte(self, b): # public method
        for i in range(8):
            GPIO.output(self.dataPin, b & (1<<i))
            self.__ping(self.clockPin) # add bit to register
        self.__ping(self.latchPin) # send register to output