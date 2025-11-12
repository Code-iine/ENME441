
import time
import multiprocessing
from shifter import Shifter   # your custom 74HC595 class

class Stepper:
    # Shared across all steppers
    num_steppers = 0
    shifter_outputs = multiprocessing.Value('I', 0)  # shared 32-bit int
    seq = [0b0001, 0b0011, 0b0010, 0b0110,
           0b0100, 0b1100, 0b1000, 0b1001]  # half-step sequence
    delay = 1200  # microseconds
    steps_per_degree = 4096 / 360

    def __init__(self, shifter, lock):
        self.s = shifter
        self.lock = lock
        self.step_state = 0
        self.angle = 0.0
        self.start_bit = 4 * Stepper.num_steppers
        Stepper.num_steppers += 1

    def __sgn(self, x):
        return 0 if x == 0 else int(x / abs(x))

    def __step(self, direction):
        # one step in given direction
        self.step_state = (self.step_state + direction) % 8
        pattern = Stepper.seq[self.step_state] << self.start_bit
        mask = 0b1111 << self.start_bit

        # update shared outputs
        with self.lock:
            cur = Stepper.shifter_outputs.value
            cur &= ~mask          # clear this motor's 4 bits
            cur |= pattern        # set new pattern
            Stepper.shifter_outputs.value = cur
            self.s.shiftByte(cur) # send to shift register

        self.angle = (self.angle + direction / Stepper.steps_per_degree) % 360
        time.sleep(Stepper.delay / 1e6)

    def __rotate(self, delta):
        direction = self.__sgn(delta)
        steps = int(abs(delta) * Stepper.steps_per_degree)
        for _ in range(steps):
            self.__step(direction)

    def rotate(self, delta):
        p = multiprocessing.Process(target=self.__rotate, args=(delta,))
        p.start()

    def goAngle(self, target):
        diff = ((target - self.angle + 180) % 360) - 180
        self.rotate(diff)

    def zero(self):
        self.angle = 0.0


# ---- Example use ----
if __name__ == '__main__':
    s = Shifter(data=16, latch=20, clock=21)
    lock = multiprocessing.Lock()

    m1 = Stepper(s, lock)
    m2 = Stepper(s, lock)

    m1.zero()
    m2.zero()

    # inital directions
    '''
    m1.goAngle(90)
    m2.goAngle(-90)
    m1.goAngle(0)
    m2.goAngle(45)
    '''
    #Problem 3 directions
    m1.zero()
    m2.zero()
    m1.goAngle(90)
    m1.goAngle(-45)
    m2.goAngle(-90)
    m2.goAngle(45)
    m1.goAngle(-135)
    m1.goAngle(135)
    m1.goAngle(0)

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nProgram ended.")
