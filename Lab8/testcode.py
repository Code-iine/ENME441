# stepper_class_shiftregister_threading.py
#
# Stepper class
#
# Switched from multiprocessing to threading.
# The task is I/O-bound (due to time.sleep), which releases the GIL.
# This allows threads to run concurrently and avoids all
# multiprocessing memory-sharing issues.

import time
import threading  # <-- 1. Use threading
from shifter import Shifter   # our custom Shifter class

class Stepper:
    """
    Supports operation of an arbitrary number of stepper motors using
    one or more shift registers.
    """

    # Class attributes:
    num_steppers = 0      # track number of Steppers instantiated
    shifter_outputs = 0   # <-- 2. Use a simple class attribute for shared state
    seq = [0b0001,0b0011,0b0010,0b0110,0b0100,0b1100,0b1000,0b1001] # CCW sequence
    delay = 1200          # delay between motor steps [us]
    steps_per_degree = 4096/360    # 4096 steps/rev * 1/360 rev/deg

    # --- 3. Simplified __init__ ---
    def __init__(self, shifter, lock):
        self.s = shifter           # shift register
        self.angle = 0             # current output shaft angle
        self.step_state = 0        # track position in sequence
        self.shifter_bit_start = 4*Stepper.num_steppers  # starting bit position
        self.lock = lock           # This will be a threading.Lock
        # No more shared_outputs 'Value' object needed
        Stepper.num_steppers += 1

    # Signum function:
    def __sgn(self, x):
        if x == 0: return(0)
        else: return(int(abs(x)/x))

    # --- 4. __step__ uses the class attribute ---
    def __step(self, dir):
        self.step_state += dir    # increment/decrement the step
        self.step_state %= 8      # ensure result stays in [0,7]
        
        new_motor_bits = Stepper.seq[self.step_state] << self.shifter_bit_start
        keep_mask = ~(0b1111 << self.shifter_bit_start)

        # --- CRITICAL SECTION ---
        # All threads share the same lock, so this is safe
        self.lock.acquire()
        
        # Read/write the shared class attribute
        current_state = Stepper.shifter_outputs
        cleared_state = current_state & keep_mask
        new_state = cleared_state | new_motor_bits
        Stepper.shifter_outputs = new_state
        
        # All threads share the *exact same* self.s object
        self.s.shiftByte(new_state)
        
        self.lock.release()
        # --- END CRITICAL SECTION ---
        
        self.angle += dir/Stepper.steps_per_degree
        self.angle %= 360         # limit to [0,359.9+] range

    # Move relative angle from current position:
    def __rotate(self, delta):
        numSteps = int(Stepper.steps_per_degree * abs(delta))
        dir = self.__sgn(delta)
        for s in range(numSteps):
            self.__step(dir)
            # time.sleep() RELEASES THE GIL, allowing other threads
            # to run their __step() method.
            time.sleep(Stepper.delay/1e6)

    # --- 5. Use threading.Thread ---
    def rotate(self, delta):
        time.sleep(0.1)
        p = threading.Thread(target=self.__rotate, args=(delta,))
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

    # --- 6. Use threading.Lock ---
    lock = threading.Lock()

    # Instantiate 2 Steppers, passing them the same lock
    # They both automatically share the class attribute 'shifter_outputs'
    # and the 's' object.
    m1 = Stepper(s, lock)
    m2 = Stepper(s, lock)

    # Zero the motors:
    m1.zero()
    m2.zero()

    # These will now run simultaneously
    m1.rotate(-90)
    m2.rotate(180)
    
    m1.rotate(45)
    m2.rotate(-45)
    
    m1.rotate(-90)
    m2.rotate(45)

    m1.rotate(45)
    m2.rotate(-90)
 
    # While the motors are running in their separate threads, the main
    # code can continue doing its thing: 
    try:
        while True:
            pass
    except:
        print('\nend')