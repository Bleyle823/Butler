"""Hold the Berkeley Humanoid Lite at its URDF rest pose.

The converted PROTO has no position controller. Without one, every joint is
free and the robot collapses. This process commands each motor to 0.
"""

from controller import Robot


def main():
    robot = Robot()
    timestep = int(robot.getBasicTimeStep())
    for index in range(robot.getNumberOfDevices()):
        device = robot.getDeviceByIndex(index)
        if not hasattr(device, "setPosition") or not hasattr(device, "setVelocity"):
            continue
        device.setVelocity(2.0)
        device.setPosition(0.0)
    while robot.step(timestep) != -1:
        pass


if __name__ == "__main__":
    main()
