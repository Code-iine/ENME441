# stepper_class_shiftregister_multiprocessing.py
#
# Stepper class
#
# Because only one motor action is allowed at a time, multithreading could be
# used instead of multiprocessing. However, the GIL makes the motor process run 
# too slowly on the Pi Zero, so multiprocessing is needed.

import time
import multiprocessing
from shifter import Shifter   # our custom Shifter class (assumed)

# --- This is a placeholder for the Shifter class ---
# (The user's code imports this, so we need a mock class for this to be runnable)
class Shifter:
    def __init__(self, data, latch, clock):
        print(f"Shifter initialized with data={data}, latch={latch}, clock={clock}")
    def shiftByte(self, byte_val):
        # In a real scenario, this would shift the byte to the register.
        # We print it to show the combined state.
        # Use {byte_val:08b} to show all 8 bits, padding with zeros.
        print(f"Shifting byte: {byte_val:08b}")
# --- End of placeholder ---


class Stepper:
    """
    Supports operation of an arbitrary number of stepper motors using
    one or more shift registers.
  
    A class attribute (shifter_outputs) keeps track of all
    shift register output values for all motors.  In addition to
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
    num_steppers = 0      # track number of Steppers instantiated
    shifter_outputs = 0   # track shift register outputs for all motors
    seq = [0b0001,0b0011,0b0010,0b0110,0b0100,0b1100,0b1000,0b1001] # CCW sequence
    delay = 1200          # delay between motor steps [us]
    steps_per_degree = 4096/360    # 4096 steps/rev * 1/360 rev/deg

    def __init__(self, shifter, lock):
        self.s = shifter           # shift register
        self.angle = 0             # current output shaft angle
        self.step_state = 0        # track position in sequence
        self.shifter_bit_start = 4*Stepper.num_steppers  # starting bit position
        self.lock = lock           # multiprocessing lock

        Stepper.num_steppers += 1   # increment the instance count

    # Signum function:
    def __sgn(self, x):
        if x == 0: return(0)
        else: return(int(abs(x)/x))

    # Move a single +/-1 step in the motor sequence:
    def __step(self, dir):
        self.step_state += dir    # increment/decrement the step
        self.step_state %= 8      # ensure result stays in [0,7]

        # --- MODIFICATION START ---
        # This entire read-modify-write block must be atomic
        # to prevent race conditions between motor processes.
        self.lock.acquire()
        try:
            # 1. Get the new 4-bit pattern for this motor, shifted to position
            pattern = Stepper.seq[self.step_state] << self.shifter_bit_start

            # 2. Create a "clear mask" to zero out *only* this motor's 4 bits
            #    (e.g., 0b11110000 for m1, 0b00001111 for m2)
            mask = 0b1111 << self.shifter_bit_start
            clear_mask = ~mask

            # 3. Clear this motor's old bits, preserving all other motor bits
            Stepper.shifter_outputs &= clear_mask
            # 4. Set this motor's new bits
            Stepper.shifter_outputs |= pattern

            # 5. Shift the new combined byte to the register
            self.s.shiftByte(Stepper.shifter_outputs)
        finally:
            self.lock.release()
        # --- MODIFICATION END ---
        
        self.angle += dir/Stepper.steps_per_degree
        self.angle %= 360         # limit to [0,359.9+] range

    # Move relative angle from current position:
    def __rotate(self, delta):
        # --- MODIFICATION START ---
        # The lock is moved to __step() to allow loops to run in parallel
        # self.lock.acquire()                 # <-- REMOVED
        numSteps = int(Stepper.steps_per_degree * abs(delta))    # find the right # of steps
        dir = self.__sgn(delta)        # find the direction (+/-1)
        for s in range(numSteps):      # take the steps
            self.__step(dir)
            time.sleep(Stepper.delay/1e6)
        # self.lock.release()           # <-- REMOVED
        # --- MODIFICATION END ---

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

    s = Shifter(data=16,latch=20,clock=21)   # set up Shifter

    # Use multiprocessing.Lock() to prevent motors from trying to 
    # execute multiple operations at the same time:
    lock = multiprocessing.Lock()

    # Instantiate 2 Steppers:
    m1 = Stepper(s, lock)
    m2 = Stepper(s, lock)

    # Zero the motors:
    m1.zero()
    m2.zero()

    # Move as desired, with eacg step occuring as soon as the previous 
    # step ends:
    m1.rotate(-90)
    m1.rotate(45)
    m1.rotate(-90)
    m1.rotate(45)

    # If separate multiprocessing.lock objects are used, the second motor
    # will run in parallel with the first motor:
    # (NOTE: With our changes, they will now run in parallel even
    # with the *same* lock, because the lock is only for one step.)
    m2.rotate(180)
    m2.rotate(-45)
    m2.rotate(45)
    m2.rotate(-90)
 
    # While the motors are running in their separate processes, the main
    # code can continue doing its thing: 
    try:
        # Give the processes time to run
        print("Main thread running... motors are moving in parallel.")
        print("Press Ctrl+C to end.")
        while True:
            time.sleep(1) # Use sleep instead of pass to reduce CPU usage
    except KeyboardInterrupt:
        print('\nend')