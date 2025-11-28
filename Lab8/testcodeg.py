import time
import multiprocessing
import RPi.GPIO as GPIO
from shifter import Shifter 

# --- STEPPER CLASS ---
class Stepper:
    # Class attributes:
    num_steppers = 0      
    shifter_outputs = multiprocessing.Value('I', 0)
    seq = [0b0001,0b0011,0b0010,0b0110,0b0100,0b1100,0b1000,0b1001]
    delay = 1200          
    steps_per_degree = 4096/360    

    def __init__(self, shifter, lock):
        self.s = shifter           
        self.angle = multiprocessing.Value('d', 0.0)
        self.step_state = 0        
        self.shifter_bit_start = 4 * Stepper.num_steppers
        self.lock = lock           
        Stepper.num_steppers += 1   

    def __sgn(self, x):
        return 0 if x == 0 else int(abs(x)/x)

    def __step(self, dir):
        self.step_state += dir    
        self.step_state %= 8      

        mask = 0b1111 << self.shifter_bit_start
        new_bits = Stepper.seq[self.step_state] << self.shifter_bit_start
        
        # Critical Section: Update Shift Register
        with self.lock:
            cur = Stepper.shifter_outputs.value
            cur &= ~mask          
            cur |= new_bits       
            Stepper.shifter_outputs.value = cur
            self.s.shiftByte(cur) 
            
            # Update angle safely
            self.angle.value = (self.angle.value + dir/Stepper.steps_per_degree) % 360

    # INTERNAL rotate function (Do the work)
    def _do_rotation(self, delta):
        numSteps = int(Stepper.steps_per_degree * abs(delta))
        dir = self.__sgn(delta)
        for s in range(numSteps):
            self.__step(dir)
            time.sleep(Stepper.delay/1e6)

    # PUBLIC rotate: NOW BLOCKING (Run in current process)
    def rotate(self, delta):
        # We removed the multiprocessing.Process here!
        # This allows us to stack commands in a wrapper function.
        self._do_rotation(delta)

    def goAngle(self, target_angle):
        # Calculate shortest path
        current = self.angle.value
        delta = ((target_angle - current + 180) % 360) - 180 
        self.rotate(delta)

    def zero(self):
        self.angle.value = 0.0

# --- SEQUENCE DEFINITIONS ---
# We define functions that run the specific list of moves for each motor
def run_m1_sequence(motor):
    # Motor 1 Moves
    motor.goAngle(90)
    motor.goAngle(-45)
    motor.goAngle(-135)
    motor.goAngle(135)
    motor.goAngle(0)

def run_m2_sequence(motor):
    # Motor 2 Moves
    motor.goAngle(-90)
    motor.goAngle(45)

# --- MAIN ---
if __name__ == '__main__':
    try:
        GPIO.setmode(GPIO.BCM)
        s = Shifter(data=16, latch=20, clock=21)
        lock = multiprocessing.Lock()

        # Instantiate Steppers
        m1 = Stepper(s, lock)
        m2 = Stepper(s, lock)

        m1.zero()
        m2.zero()

        print("Starting Simultaneous Movement...")

        # Create TWO processes:
        # One controls M1 entirely, One controls M2 entirely.
        p1 = multiprocessing.Process(target=run_m1_sequence, args=(m1,))
        p2 = multiprocessing.Process(target=run_m2_sequence, args=(m2,))

        # Start them at the same time
        p1.start()
        p2.start()

        # Wait for both to finish
        p1.join()
        p2.join()

        print("All sequences complete.")

    except KeyboardInterrupt:
        print('\nStopping motors...')
    finally:
        # CLEANUP IS CRITICAL
        GPIO.cleanup()
        print('GPIO pins released.')