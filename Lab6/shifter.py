import RPi.GPIO as GPIO
import time
import random

GPIO.setmode(GPIO.BCM)
serialPin = 23
latchPin = 24
clockPin = 25

class Shifter:
    def __init__(self,serialPin,latchPin,clockPin):
       self.serialPin = serialPin
       self.latchPin = latchPin
       self.clockPin = clockPin

       GPIO.setup(self.serialPin, GPIO.OUT)
       GPIO.setup(self.latchPin, GPIO.OUT, initial=0)  # start latch & clock low
       GPIO.setup(self.clockPin, GPIO.OUT, initial=0)  
       
       pattern = 0b01100110        # 8-bit pattern to display on LED bar

    def __ping(self, p): #private method
        GPIO.output(p,1)
        time.sleep(0)
        GPIO.output(p,0)

    def shiftByte(self, b): # public method
        for i in range(8):
            GPIO.output(self.serialPin, b & (1<<i))
            self.__ping(self.clockPin) # add bit to register
        self.__ping(self.latchPin) # send register to output

class Bug:
    range = [1, -1]
    starter = 0
    switch = 0

    def __init__(self,timestep = 0.1,x = 3,isWrapOn = False,):
        self.timestep = timestep
        self.x = x
        self.isWrapOn = isWrapOn
        self.__shifter = Shifter(serialPin,latchPin,clockPin)


    def start(self):
        if self.switch == 1:
            step = random.choice([1, -1])
            walk = self.x + step

            if self.isWrapOn == True:
                if self.x > 8:
                    self.x = 1
                elif self.x < 0:
                    self.x = 8
            else:
                if walk > 0 and walk < 8:
                    self.x = walk

            self.__shifter.shiftByte(1<<self.x)
            time.sleep(self.timestep) #0.05 seconds

            '''
            for i in range(108):
                Shifter1.shiftByte(i)
                time.sleep(0.5)
                '''
        else:
            return
            
    def stop(self):
        self.starter = 0
        self.__shifter.shiftByte(0)
        #GPIO.cleanup()
    
    def switch_on(self):
        self.switch = 1

    def switch_off(self):
        self.switch = 0

    def flip_state(self):
        if self.isWrapOn == False:
            self.isWrapOn = True
        else:
            self.isWrapOn = False





