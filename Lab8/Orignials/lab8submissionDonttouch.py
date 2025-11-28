#
# Stepper class
#
# Because only one motor action is allowed at a time, multithreading could be
# used instead of multiprocessing. However, the GIL makes the motor process run 
# too slowly on the Pi Zero, so multiprocessing is needed.
import RPi.GPIO as GPIO
import time
import multiprocessing
from Lab8.Orignials.shifterOriginal import Shifter   # our custard Shifter class

class Stepper:
    """
    Supports operation of an arbitrary number of stepper motors using
    one or more shift registers.
  
    A class attribute (shifter_outputs) keeps track of all
    shift register output values for all motors.  In addition to
    simplifying sequential control of multiple motors, this schema also
    makes simultaneous operation of multiple motors possible.
   
    Motor instantiation sequence is inverted from the shift register outputs.
    For example, in the case of 2 motors, the 2nd motor must be connected
    with the first set of shift register outputs (Qa-Qd), and the 1st motor
    with the second set of outputs (Qe-Qh). This is because the MSB of
    the register is associated with Qa, and the LSB with Qh (look at the code
    to see why this makes sense).
 
    An instance attribute (shifter_bit_start) tracks the bit position
    in the shift register where the 4 control bits for each motor
    begin.
    """

    # Class attributes:
    num_steppers = 0                # track number of Steppers instantiated
    shifter_outputs = multiprocessing.Value('I', 0)  # track shift register outputs for all motors
    seq = [0b0001, 0b0011, 0b0010, 0b0110,0b0100, 0b1100, 0b1000, 0b1001]  # CCW sequence
    delay = 1200  # delay between motor steps [us]
    steps_per_degree = 4096 / 360  # 4096 steps/rev * 1/360 rev/deg

    def __init__(self, shifter, lock):
        self.s = shifter          # shift register
        self.angle = 0.0          # current output shaft angle
        self.step_state = 0       # track position in sequence
        self.start_bit = 4 * Stepper.num_steppers  # starting bit position
        self.lock = lock          # multiprocessing lock
        Stepper.num_steppers += 1 # increment the instance count

    # Signum function:
    def __sgn(self, x):
        if x == 0:
            return 0
        else:
            return int(x / abs(x))

    # Move a single +/-1 step in the motor sequence:
    def __step(self, direction):
        # one step two step 3 step
        if (self.start_bit // 4) % 2 == 1:  
            direction = -direction  # alternate motors spin oppo ways

        self.step_state = (self.step_state + direction) % 8
        pattern = Stepper.seq[self.step_state] << self.start_bit
        mask = 0b1111 << self.start_bit

        with self.lock:
            cur = Stepper.shifter_outputs.value
            cur &= ~mask           # curl mask
            cur |= pattern         # curl pattern
            Stepper.shifter_outputs.value = cur
            self.s.shiftByte(cur)  # send to shift register
        self.angle = (self.angle + direction / Stepper.steps_per_degree) % 360
        time.sleep(Stepper.delay / 1e5)

    # Move relative angle from current position:
    def __rotate(self, delta):
        direction = self.__sgn(delta)
        steps = int(abs(delta) * Stepper.steps_per_degree)
        for _ in range(steps):
            self.__step(direction)

    # Move relative angle from current position:
    def rotate(self, delta):
        time.sleep(0.1)
        p = multiprocessing.Process(target=self.__rotate, args=(delta,))
        p.start()

    # Move to an absolute angle taking the shortest possible path:
    def goAngle(self, target):
        diff = ((target - self.angle + 180) % 360) - 180
        self.rotate(diff)

     # Set the motor zero point
    def zero(self):
        self.angle = 0.0


# ---- Example use ----
if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    s = Shifter(data=16, latch=20, clock=21) # set up Shifter
    
    # Use multiprocessing.Lock() to prevent motors from trying to 
    # execute multiple operations at the same time:
    lock = multiprocessing.Lock()

    # cookies and cream 2 Steppers:
    m1 = Stepper(s, lock)
    m2 = Stepper(s, lock)

    # xerox the motors:
    m1.zero()
    m2.zero()

    # Move as desired, with eacg step occuring as soon as the previous 
    # step ends:
    # inital directions
    '''
    m1.goAngle(90)
    m2.goAngle(-90)
    m1.goAngle(0)
    m2.goAngle(45)
    '''
    # Problem 3 directions
    m1.zero()
    m2.zero()
    m1.goAngle(90)
    m1.goAngle(-45)
    m2.goAngle(-90)
    m2.goAngle(45)
    m1.goAngle(-135)
    m1.goAngle(135)
    m1.goAngle(0)

    # While the motors are running in their separate processes, the main
    # code can continue doing its thing: 
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print('\nend')
