# Lab 8 p2
# stepper_class_shiftregister_multiprocessing.py
#
# Stepper class
#
# Because only one motor action is allowed at a time, multithreading could be
# used instead of multiprocessing. However, the GIL makes the motor process run 
# too slowly on the Pi Zero, so multiprocessing is needed.

import time
import multiprocessing
import RPi.GPIO as GPIO
from shifter import Shifter   # our custom Shifter class

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
    num_steppers = 0      # track number of Steppers instantiated
    # CHANGED: make shared across processes
    shifter_outputs = multiprocessing.Value('I', 0)   # track shift register outputs for all motors
    seq = [0b0001,0b0011,0b0010,0b0110,0b0100,0b1100,0b1000,0b1001] # CCW sequence
    delay = 1200          # delay between motor steps [us]
    steps_per_degree = 4096/360    # 4096 steps/rev * 1/360 rev/deg

    def __init__(self, shifter, lock):
        self.s = shifter           # shift register
        # self.angle = 0             # current output shaft angle
        self.angle = multiprocessing.Value('d', 0.0)
        self.step_state = 0        # track position in sequence
        self.shifter_bit_start = 4*Stepper.num_steppers  # starting bit position
        self.lock = lock           # multiprocessing lock

        Stepper.num_steppers += 1   # increment the instance count

    # Signum function:
    def __sgn(self, x):
        if x == 0: return(0)
        else: return(int(abs(x)/x))

    # Move a single +/-1 step in the motor sequence:
    def __step(self, dir):
        self.step_state += dir    # increment/decrement the step
        self.step_state %= 8      # ensure result stays in [0,7]

        # CHANGED: update only our 4-bit nibble under a tiny critical section
        mask = 0b1111 << self.shifter_bit_start
        new_bits = Stepper.seq[self.step_state] << self.shifter_bit_start
        with self.lock:
            cur = Stepper.shifter_outputs.value
            cur &= ~mask          # clear only our nibble
            cur |= new_bits       # set our new pattern
            Stepper.shifter_outputs.value = cur
            self.s.shiftByte(cur) # push combined outputs
            self.angle.value = (self.angle.value + dir/Stepper.steps_per_degree) % 360

        #self.angle += dir/Stepper.steps_per_degree
        #self.angle %= 360         # limit to [0,359.9+] range

    # Move relative angle from current position:
    def __rotate(self, delta):
        # CHANGED: do not hold the lock for the entire move; let motors interleave
        numSteps = int(Stepper.steps_per_degree * abs(delta))    # find the right # of steps
        dir = self.__sgn(delta)        # find the direction (+/-1)
        for s in range(numSteps):      # take the steps
            self.__step(dir)
            time.sleep(Stepper.delay/1e6)

    # Move relative angle from current position:
    def rotate(self, delta):
        time.sleep(0.1)
        p = multiprocessing.Process(target=self.__rotate, args=(delta,))
        p.start()

    # Move to an absolute angle taking the shortest possible path:
    def goAngle(self, angle):
        current = self.angle.value
        delta = ((angle - current + 180) % 360) - 180 # maps the difference into the interval (−180, 180), so the motor always chooses the shortest direction
        self.rotate(delta)
    

    # Set the motor zero point
    def zero(self):
        self.angle.value = 0.0


# Example use:
if __name__ == '__main__':
    try:
        GPIO.setmode(GPIO.BCM)
        s = Shifter(data=16, latch=20, clock=21)
        lock = multiprocessing.Lock()
        
        m1 = Stepper(s, lock)
        m2 = Stepper(s, lock)

        m1.zero()
        m2.zero()

        print("Starting simultaneous moves...")
        
        # Create processes manually so we can start them together
        # Example: Move m1 to 90 and m2 to -90 at the same time
        p1 = multiprocessing.Process(target=m1.goAngle, args=(90,))
        p2 = multiprocessing.Process(target=m2.goAngle, args=(-90,))
        
        p1.start()
        p2.start()
        
        # Wait for both to finish before sending next command
        p1.join()
        p2.join()
        
        print("Move complete. Doing next move...")
        
        # Next move
        p3 = multiprocessing.Process(target=m1.goAngle, args=(-45,))
        p3.start()
        p3.join()

    except KeyboardInterrupt:
        print('\nStopping...')
    finally:
        GPIO.cleanup()
        print('GPIO released.')