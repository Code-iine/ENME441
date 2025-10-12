import RPi.GPIO as GPIO
import time
import math

GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT)
pwm4 = GPIO.PWM(4, 500)          # create PWM object @ 100 Hz
GPIO.setup(5, GPIO.OUT)
pwm5 = GPIO.PWM(5, 500)
GPIO.setup(6, GPIO.OUT)
pwm6 = GPIO.PWM(6, 500)
GPIO.setup(7, GPIO.OUT)
pwm7 = GPIO.PWM(7, 500)
GPIO.setup(8, GPIO.OUT)
pwm8 = GPIO.PWM(8, 500)
GPIO.setup(9, GPIO.OUT)
pwm9 = GPIO.PWM(9, 500)
GPIO.setup(10, GPIO.OUT)
pwm10 = GPIO.PWM(10, 500)
GPIO.setup(11, GPIO.OUT)
pwm11= GPIO.PWM(11, 500)
GPIO.setup(12, GPIO.OUT)
pwm12 = GPIO.PWM(12, 500)
GPIO.setup(13, GPIO.OUT)
pwm13 = GPIO.PWM(13, 500)

GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

f = 0.2

switch = 0

def forward(pin):
      global switch
      if GPIO.input(21) == GPIO.HIGH:
       switch = 0
      else:
       switch = 1
    

GPIO.add_event_detect(21, GPIO.BOTH, callback=forward, bouncetime=100)

try:
  pwm4.start(0)                  # initiate PWM at 0% duty cycle
  pwm5.start(0)
  pwm6.start(0)
  pwm7.start(0)
  pwm8.start(0)
  pwm9.start(0)
  pwm10.start(0)
  pwm11.start(0)
  pwm12.start(0)
  pwm13.start(0)

  while True:
    if switch != 1:
      t = time.time()
      B = ((math.sin(2*math.pi*f*t))**2)*100
      pwm4.ChangeDutyCycle(B)
      t = time.time()
      B = ((math.sin(2*math.pi*f*t - (math.pi/11)))**2)*100
      pwm5.ChangeDutyCycle(B)
      t = time.time()
      B = ((math.sin(2*math.pi*f*t - 2*(math.pi/11)))**2)*100
      pwm6.ChangeDutyCycle(B)
      t = time.time()
      B = ((math.sin(2*math.pi*f*t - 3*(math.pi/11)))**2)*100
      pwm7.ChangeDutyCycle(B)
      t = time.time()
      B = ((math.sin(2*math.pi*f*t - 4*(math.pi/11)))**2)*100
      pwm8.ChangeDutyCycle(B)
      t = time.time()
      B = ((math.sin(2*math.pi*f*t - 5*(math.pi/11)))**2)*100
      pwm9.ChangeDutyCycle(B)
      t = time.time()
      B = ((math.sin(2*math.pi*f*t - 6*(math.pi/11)))**2)*100
      pwm10.ChangeDutyCycle(B)
      t = time.time()
      B = ((math.sin(2*math.pi*f*t - 7*(math.pi/11)))**2)*100
      pwm11.ChangeDutyCycle(B)
      t = time.time()
      B = ((math.sin(2*math.pi*f*t - 8*(math.pi/11)))**2)*100
      pwm12.ChangeDutyCycle(B)
      t = time.time()
      B = ((math.sin(2*math.pi*f*t - 9*(math.pi/11)))**2)*100
      pwm13.ChangeDutyCycle(B)
        
    else:
        t = time.time()
        B = ((math.sin(2*math.pi*f*t))**2)*100
        pwm4.ChangeDutyCycle(B)
        t = time.time()
        B = ((math.sin(2*math.pi*f*t + (math.pi/11)))**2)*100
        pwm5.ChangeDutyCycle(B)
        t = time.time()
        B = ((math.sin(2*math.pi*f*t + 2*(math.pi/11)))**2)*100
        pwm6.ChangeDutyCycle(B)
        t = time.time()
        B = ((math.sin(2*math.pi*f*t + 3*(math.pi/11)))**2)*100
        pwm7.ChangeDutyCycle(B)
        t = time.time()
        B = ((math.sin(2*math.pi*f*t + 4*(math.pi/11)))**2)*100
        pwm8.ChangeDutyCycle(B)
        t = time.time()
        B = ((math.sin(2*math.pi*f*t + 5*(math.pi/11)))**2)*100
        pwm9.ChangeDutyCycle(B)
        t = time.time()
        B = ((math.sin(2*math.pi*f*t + 6*(math.pi/11)))**2)*100
        pwm10.ChangeDutyCycle(B)
        t = time.time()
        B = ((math.sin(2*math.pi*f*t + 7*(math.pi/11)))**2)*100
        pwm11.ChangeDutyCycle(B)
        t = time.time()
        B = ((math.sin(2*math.pi*f*t + 8*(math.pi/11)))**2)*100
        pwm12.ChangeDutyCycle(B)
        t = time.time()
        B = ((math.sin(2*math.pi*f*t + 9*(math.pi/11)))**2)*100
        pwm13.ChangeDutyCycle(B)


except KeyboardInterrupt:       # stop gracefully on ctrl-C
  print('\nExiting')

pwm.stop()
GPIO.cleanup()
