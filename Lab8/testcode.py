# stepper_class_shiftregister_multiprocessing.py
#
# Stepper class
#
# Because only one motor action is allowed at a time, multithreading could be
# used instead of multiprocessing. However, the GIL makes the motor process run 
# too slowly on the Pi Zero, so multiprocessing is needed.

import time
import multiprocessing
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
    shifter_outputs = 0   # track shift register outputs for all motors
    seq = [0b0001,0b0011,0b0010,0b0110,0b0100,0b1100,0b1000,0b1001] # CCW sequence
    delay = 1200          # delay between motor steps [us]
    steps_per_degree = 4096/360    # 4096 steps/rev * 1/360 rev/deg

    def __init__(self, shifter, lock):
        self.s = shifter           # shift register
        self.angle = 0             # current output shaft angle
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
        
        # --- MODIFIED BITWISE LOGIC ---
        # This new logic allows simultaneous operation by ensuring
        # we only modify the 4 bits relevant to *this* motor,
        # leaving all other motor bits untouched.
        
        # 1. Get the new 4-bit step pattern, shifted to this motor's position
        new_motor_bits = Stepper.seq[self.step_state] << self.shifter_bit_start

        # 2. Create an inverted mask to *clear* only this motor's 4 bits
        #    e.g., motor 0 (offset 0): mask = ...1111111111110000
        #    e.g., motor 1 (offset 4): mask = ...1111111100001111
        keep_mask = ~(0b1111 << self.shifter_bit_start)

        # 3. --- CRITICAL SECTION ---
        #    Acquire lock to prevent race condition (read-modify-write)
        self.lock.acquire()
        
        # 4. Read the current state of ALL motors
        current_state = Stepper.shifter_outputs
        
        # 5. Clear just this motor's bits, keeping all others
        cleared_state = current_state & keep_mask
        
        # 6. Set this motor's new bits
        new_state = cleared_state | new_motor_bits
        
        # 7. Update the shared class attribute
        Stepper.shifter_outputs = new_state
        
        # 8. Write the new combined state to the hardware
        self.s.shiftByte(Stepper.shifter_outputs)
        
        # 9. Release the lock so other motors can step
        self.lock.release()
        # --- END CRITICAL SECTION ---
        
        self.angle += dir/Stepper.steps_per_degree
        self.angle %= 360         # limit to [0,359.9+] range

    # Move relative angle from current position:
    def __rotate(self, delta):
        # ** MODIFIED: Removed lock **
        # The lock is now inside __step() to protect the
        # shared resource, allowing this loop to run in parallel.
        # self.lock.acquire()                 
        numSteps = int(Stepper.steps_per_degree * abs(delta))    # find the right # of steps
        dir = self.__sgn(delta)        # find the direction (+/-1)
        for s in range(numSteps):      # take the steps
            self.__step(dir)
            time.sleep(Stepper.delay/1e6)
        # self.lock.release()

    # Move relative angle from current position:
    def rotate(self, delta):
        time.sleep(0.1)
        p = multiprocessing.Process(target=self.__rotate, args=(delta,))
        p.start()

    # Move to an absolute angle taking the shortest possible path:
    def goAngle(self, angle):
         pass
         # COMPLETE THIS METHOD FOR LAB 8

    # Set the motor zero point
    def zero(self):
        self.angle = 0


# Example use:

if __name__ == '__main__':

    s = Shifter(data=16,latch=20,clock=21)   # set up Shifter

    # Use a *single* multiprocessing.Lock() to prevent motors from 
    # writing to the shared 'shifter_outputs' at the same time.
    lock = multiprocessing.Lock()

    # Instantiate 2 Steppers:
    m1 = Stepper(s, lock)
    m2 = Stepper(s, lock)

    # Zero the motors:
    m1.zero()
    m2.zero()

    # Move as desired. With the new changes, m1 and m2 will
    # now run their sequences simultaneously.
    m1.rotate(-90)
    m1.rotate(45)
    m1.rotate(-90)
    m1.rotate(45)

    # These m2 commands will also run in parallel with the m1
    # commands, as each .rotate() call spawns a new process
    # that runs in the background.
    m2.rotate(180)
    m2.rotate(-45)
    m2.rotate(45)
    m2.rotate(-90)
 
    # While the motors are running in their separate processes, the main
    # code can continue doing its thing: 
    try:
        while True:
            pass
    except:
        print('\nend')