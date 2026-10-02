"""Hinged hotel door. Closed by default. Open/close via customData or keyboard."""

from controller import Robot

OPEN_POS = 1.45
CLOSED_POS = 0.0
SPEED = 1.6


def main():
    robot = Robot()
    timestep = int(robot.getBasicTimeStep())
    motor = robot.getDevice("hinge")
    sensor = robot.getDevice("hinge_sensor")
    if sensor is not None:
        sensor.enable(timestep)
    motor.setVelocity(SPEED)
    motor.setPosition(CLOSED_POS)
    keyboard = robot.getKeyboard()
    keyboard.enable(timestep)
    target = CLOSED_POS

    while robot.step(timestep) != -1:
        cmd = (robot.getCustomData() or "").strip().lower()
        if cmd in ("open", "1", "true"):
            target = OPEN_POS
        elif cmd in ("close", "0", "false"):
            target = CLOSED_POS

        key = keyboard.getKey()
        while key != -1:
            if key in (ord("O"), ord("o")):
                target = OPEN_POS
            elif key in (ord("C"), ord("c")):
                target = CLOSED_POS
            elif key in (ord("T"), ord("t")):
                target = CLOSED_POS if abs(target - OPEN_POS) < 0.2 else OPEN_POS
            key = keyboard.getKey()

        motor.setPosition(target)


if __name__ == "__main__":
    main()
