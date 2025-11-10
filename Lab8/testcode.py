# stepper_class_shiftregister_multiprocessing.py

import time
import multiprocessing
from shifter import Shifter   # our custom Shifter class

class Stepper:
    """
    Supports operation of an arbitrary number of stepper motors using
    one or more shift registers.
    """

    # Class attributes:
    num_steppers = 0      # track number of Steppers instantiated
    
    # --- CHANGE 1: REMOVED CLASS ATTRIBUTE ---
    # shifter_outputs = 0   <-- This is gone. It will be an instance attribute
    #                         pointing to a shared memory object.
    
    seq = [0b0001,0b0011,0b0010,0b0110,0b0100,0b1100,0b1000,0b1001] # CCW sequence
    delay = 1200          # delay between motor steps [us]
    steps_per_degree = 4096/360    # 4096 steps/rev * 1/360 rev/deg

    # --- CHANGE 2: UPDATED __init__ ---
    def __init__(self, shifter, lock, shared_outputs):
        self.s = shifter           # shift register
        self.angle = 0             # current output shaft angle
        self.step_state = 0        # track position in sequence
        self.shifter_bit_start = 4*Stepper.num_steppers  # starting bit position
        self.lock = lock           # multiprocessing lock
        
        # Store the shared memory Value object
        self.shifter_outputs = shared_outputs

        Stepper.num_steppers += 1   # increment the instance count

    # Signum function:
    def __sgn(self, x):
        if x == 0: return(0)
        else: return(int(abs(x)/x))

    # Move a single +/-1 step in the motor sequence:
    # --- CHANGE 3: UPDATED __step__ ---
    def __step(self, dir):
        self.step_state += dir    # increment/decrement the step
        self.step_state %= 8      # ensure result stays in [0,7]
        
        # 1. Get the new 4-bit step pattern, shifted to this motor's position
        new_motor_bits = Stepper.seq[self.step_state] << self.shifter_bit_start

        # 2. Create an inverted mask to *clear* only this motor's 4 bits
        keep_mask = ~(0b1111 << self.shifter_bit_start)

        # 3. --- CRITICAL SECTION ---
        #    Acquire lock to protect the shared memory read/write
        self.lock.acquire()
        
        # 4. Read the *current value* from the shared memory object
        current_state = self.shifter_outputs.value
        
        # 5. Clear just this motor's bits, keeping all others
        cleared_state = current_state & keep_mask
        
        # 6. Set this motor's new bits
        new_state = cleared_state | new_motor_bits
        
        # 7. Update the shared memory object's *value*
        self.shifter_outputs.value = new_state
        
        # 8. Write the new combined state to the hardware
        #    We use new_state, not another read, for efficiency
        self.s.shiftByte(new_state)
        
        # 9. Release the lock so other motors can step
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
            time.sleep(Stepper.delay/1e6)

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
# --- CHANGE 4: UPDATED MAIN BLOCK ---
if __name__ == '__main__':

    s = Shifter(data=16,latch=20,clock=21)   # set up Shifter

    # Use multiprocessing.Lock() to prevent motors from trying to 
    # execute multiple operations at the same time:
    lock = multiprocessing.Lock()
    
    # Create a shared integer Value, initialized to 0
    # 'i' stands for integer.
    shifter_state = multiprocessing.Value('i', 0)

    # Instantiate 2 Steppers, passing them the SAME lock and shared value
    m1 = Stepper(s, lock, shifter_state)
    m2 = Stepper(s, lock, shifter_state)

    # Zero the motors:
    m1.zero()
    m2.zero()

    # These will now run truly simultaneously
    m1.rotate(-90)
    m2.rotate(180)
    
    m1.rotate(45)
    m2.rotate(-45)
    
    m1.rotate(-90)
    m2.rotate(45)

    m1.rotate(45)
    m2.rotate(-90)
 
    # While the motors are running in their separate processes, the main
    # code can continue doing its thing: 
    try:
        while True:
            pass
    except:
        print('\nend')