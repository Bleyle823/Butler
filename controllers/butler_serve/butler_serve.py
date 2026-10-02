"""ButlerServe base teleop.

Foundations for later job code: differential-drive helpers, named wheel
motors, and hooks for torso-tray seating. Does not enable the Hokuyo
(667 rays) or talk to peaq/Circle.

Select servebot-1 in Webots, then:
  arrows or WASD  drive
  Q               stop
  Shift+arrows    faster
  G               print pose
"""

import sys

from controller import Keyboard, Robot

MAX_SPEED = 4.0
FAST_SPEED = 6.4
WHEEL_RADIUS = 0.0985
WHEEL_SEP = 0.4044
SHIFT = Keyboard.SHIFT
CTRL_MASK = Keyboard.SHIFT | Keyboard.CONTROL | Keyboard.ALT


class ButlerServeController:
    def __init__(self):
        self.robot = Robot()
        self.timestep = int(self.robot.getBasicTimeStep())
        self.left = self.robot.getDevice("wheel_left_joint")
        self.right = self.robot.getDevice("wheel_right_joint")
        self.left.setPosition(float("inf"))
        self.right.setPosition(float("inf"))
        self.set_wheel_speeds(0.0, 0.0)
        self.keyboard = self.robot.getKeyboard()
        self.keyboard.enable(self.timestep)
        args = list(sys.argv[1:])
        self.parked = any(str(arg).strip().lower() == "parked" for arg in args)
        print(
            "ButlerServe '%s': arrows/WASD drive, Q stop, Shift faster, G pose."
            % self.robot.getName()
        )

    def set_wheel_speeds(self, left_rad_s, right_rad_s):
        self.left.setVelocity(left_rad_s)
        self.right.setVelocity(right_rad_s)

    def set_base_velocity(self, linear_m_s, angular_rad_s):
        left = (linear_m_s - angular_rad_s * WHEEL_SEP / 2.0) / WHEEL_RADIUS
        right = (linear_m_s + angular_rad_s * WHEEL_SEP / 2.0) / WHEEL_RADIUS
        cap = FAST_SPEED
        left = max(-cap, min(cap, left))
        right = max(-cap, min(cap, right))
        self.set_wheel_speeds(left, right)

    def read_drive_command(self):
        speed = MAX_SPEED
        linear = 0.0
        angular = 0.0
        key = self.keyboard.getKey()
        while key != -1:
            if key & SHIFT:
                speed = FAST_SPEED
            raw = key & ~CTRL_MASK
            if raw in (Keyboard.UP, ord("W"), ord("w")):
                linear += speed * WHEEL_RADIUS
            elif raw in (Keyboard.DOWN, ord("S"), ord("s")):
                linear -= speed * WHEEL_RADIUS
            elif raw in (Keyboard.LEFT, ord("A"), ord("a")):
                angular += speed * WHEEL_RADIUS / (WHEEL_SEP / 2.0)
            elif raw in (Keyboard.RIGHT, ord("D"), ord("d")):
                angular -= speed * WHEEL_RADIUS / (WHEEL_SEP / 2.0)
            elif raw in (ord("Q"), ord("q")):
                linear = 0.0
                angular = 0.0
            elif raw in (ord("G"), ord("g")):
                print(
                    "pose t=%.2f name=%s"
                    % (self.robot.getTime(), self.robot.getName())
                )
            key = self.keyboard.getKey()
        return linear, angular

    def run(self):
        while self.robot.step(self.timestep) != -1:
            if self.parked:
                self.set_wheel_speeds(0.0, 0.0)
                continue
            linear, angular = self.read_drive_command()
            self.set_base_velocity(linear, angular)


def main():
    ButlerServeController().run()


if __name__ == "__main__":
    main()
