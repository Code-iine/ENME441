# stepper_simple_version.py
# Simplified Stepper + Shift Register control with multiprocessing
# for controlling multiple steppers at once

import time
import multiprocessing
from shifter import Shifter   # custom class for 74HC595 shift register

class Stepper:
    # Class-level shared data
    num_steppers = 0
    seq = [0b0001, 0b0011, 0b0010, 0b0110,
           0b0100, 0b1100, 0b1000, 0b1001]  # half-step CCW sequence
    delay = 1200          # microseconds between steps
    steps_per_degree = 4096 / 360  # steps per degree

    def __init__(self, shifter, lock):
        self.s = shifter
        self.lock = lock
        self.step_state = 0
        self.angle = 0.0
        self.start_bit = 4 * Stepper.num_steppers  # where this motor’s bits begin
        Stepper.num_steppers += 1

    def __sgn(self, x):
        return 0 if x == 0 else int(x / abs(x))

    def __step(self, direction):
        # move one step forward or backward
        self.step_state = (self.step_state + direction) % 8
        pattern = Stepper.seq[self.step_state] << self.start_bit

        # make sure only this motor’s 4 bits are updated
        with self.lock:
            # read current outputs and update just our 4 bits
            cur = self.s.outputs
            mask = 0b1111 << self.start_bit
            cur = (cur & ~mask) | pattern
            self.s.outputs = cur
            self.s.shiftByte(cur)

        self.angle = (self.angle + direction / Stepper.steps_per_degree) % 360
        time.sleep(Stepper.delay / 1e6)

    def __rotate(self, delta):
        direction = self.__sgn(delta)
        steps = int(abs(delta) * Stepper.steps_per_degree)
        for _ in range(steps):
            self.__step(direction)

    def rotate(self, delta):
        # start a new process for each move
        p = multiprocessing.Process(target=self.__rotate, args=(delta,))
        p.start()

    def goAngle(self, angle):
        # find shortest path to new angle
        diff = ((angle - self.angle + 180) % 360) - 180
        self.rotate(diff)

    def zero(self):
        self.angle = 0.0


# ---- Example usage ----
if __name__ == '__main__':
    s = Shifter(data=16, latch=20, clock=21)
    s.outputs = 0  # add a simple variable to track output bits

    lock = multiprocessing.Lock()

    m1 = Stepper(s, lock)
    m2 = Stepper(s, lock)

    m1.zero()
    m2.zero()

    # move to various angles
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
