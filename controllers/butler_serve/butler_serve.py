"""ButlerServe: sensors, folded idle arms, autonomous pickup and delivery.

Webots never talks to peaq or Circle. This process publishes pose, battery,
pickup, and delivery on the robot customData field and accepts a job through
controllerArgs: autonomous (default), teleop, parked.

Select servebot-1:
  arrows / WASD   drive (teleop, or hold to override)
  Q               stop
  Shift+arrows    faster
  G               print pose
  J               start / restart the room-1204 pizza job
  T               toggle teleop
"""

from __future__ import annotations

import ctypes
import json
import math
import sys

from controller import Keyboard, Supervisor

MAX_SPEED = 4.0
FAST_SPEED = 6.4
WHEEL_RADIUS = 0.0985
WHEEL_SEP = 0.4044
SHIFT = Keyboard.SHIFT
CTRL_MASK = Keyboard.SHIFT | Keyboard.CONTROL | Keyboard.ALT

# Rest: both arms face back and hang down, elbows bent so the hands stay off the floor.
# Positive shoulder pitch lowers the arm. The old negative pitch held them up.
IDLE_POSE = {
    "head_1_joint": 0.0,
    "head_2_joint": -0.12,
    "torso_lift_joint": 0.16,
    "arm_right_1_joint": 1.35,
    "arm_right_2_joint": 1.15,
    "arm_right_3_joint": 0.0,
    "arm_right_4_joint": 1.75,
    "arm_right_5_joint": 0.2,
    "arm_right_6_joint": 0.0,
    "arm_right_7_joint": 0.0,
    "arm_left_1_joint": 1.45,
    "arm_left_2_joint": 1.15,
    "arm_left_3_joint": 0.1,
    "arm_left_4_joint": 1.75,
    "arm_left_5_joint": -0.2,
    "arm_left_6_joint": 0.0,
    "arm_left_7_joint": 0.0,
}

# Right arm only. Left arm stays folded in IDLE_POSE so it cannot block a turn.
# Same sequence as the p-rob3 and vacuum-gripper samples: reach, close, lift, place.
_RIGHT_JOINTS = (
    "arm_right_1_joint",
    "arm_right_2_joint",
    "arm_right_3_joint",
    "arm_right_4_joint",
    "arm_right_5_joint",
    "arm_right_6_joint",
    "arm_right_7_joint",
)
# Side reach. Joint 1 near 0 points the right arm out to the robot's right,
# where the pedestal sits. A large negative joint 1 left the hand behind the body.
REACH_RIGHT = (0.15, 0.35, 0.0, 0.70, 0.10, 0.0, 0.0)
LIFT_RIGHT = (0.12, 0.05, 0.10, 1.05, 0.45, 0.15, 0.0)
TRAY_RIGHT = (0.02, -0.45, 0.22, 1.95, 1.20, 0.55, 0.0)

# Pizza is on the pedestal at (7.55, -4.05), south of the lane. The stance is
# beside it, not against it. Plate and glass stay on the counter for later.
PICKS = (
    ("PIZZA_BOX", 7.50, -3.25),
)


def _right_pose(joints, head=0.05, torso=0.22):
    pose = dict(IDLE_POSE)
    pose["head_2_joint"] = head
    pose["torso_lift_joint"] = torso
    for name, value in zip(_RIGHT_JOINTS, joints):
        pose[name] = value
    return pose

# Robot-frame well offsets (metres) relative to the base origin.
WELLS = {
    "PIZZA_BOX": (0.36, -0.05, 0.84),
    "COUNTER_PLATE": (0.34, 0.08, 0.83),
    "COUNTER_GLASS": (0.30, 0.12, 0.86),
}

PLACE_POSES = {
    "PIZZA_BOX": (-5.2, 3.05, 0.78),
    "COUNTER_PLATE": (-5.05, 3.2, 0.73),
    "COUNTER_GLASS": (-4.9, 3.05, 0.73),
}

# Dock faces +Y. First corner is northeast of the parked row, not into the
# west-wall furniture. Then north to the lobby door latitude and through.
PATH_PICKUP = (
    (-8.40, -5.00, False),
    (-8.40, -2.10, False),
    (-7.00, -2.10, False),
    (-7.00, -0.20, False),
    ( 4.00,  0.00, False),
    ( 4.00, -1.65, True),
    ( 8.05, -1.65, False),
)
PATH_DELIVER = (
    ( 6.00, -2.30, False),
    ( 4.00, -2.20, False),
    ( 4.00,  0.00, True),
    (-7.20,  0.00, False),
    (-7.20,  2.15, True),
    (-5.40,  2.25, False),
)
PATH_DOCK = (
    (-7.20,  0.00, False),
    (-7.00, -2.00, True),
    (-8.40, -2.10, False),
    (-8.40, -5.00, False),
    (-9.60, -7.15, False),
)

WAYPOINT_TOL = 0.28
GOAL_TOL = 0.48
CRUISE = 0.55
TURN_IN_PLACE = 1.25
HEADING_ALIGN = 0.40
FRONT_STOP = 0.28
STUCK_TIME = 4.5


class ButlerServeController:
    def __init__(self):
        self.robot = Supervisor()
        self.timestep = int(self.robot.getBasicTimeStep())
        self.name = self.robot.getName()
        self.left = self.robot.getDevice("wheel_left_joint")
        self.right = self.robot.getDevice("wheel_right_joint")
        self.left.setPosition(float("inf"))
        self.right.setPosition(float("inf"))
        self.set_wheel_speeds(0.0, 0.0)
        self.keyboard = self.robot.getKeyboard()
        self.keyboard.enable(self.timestep)
        args = [str(a).strip().lower() for a in sys.argv[1:]]
        self.parked = "parked" in args
        self.teleop = "teleop" in args or self.parked
        self.battery = 1.0
        self.event = "idle"
        self.carried = []
        self.pose_hold_until = 0.0
        self.waypoints = []
        self.wp_index = 0
        self.job = None
        self._keys_held = set()
        self._stuck_since = None
        self._stuck_pose = None
        self._recover_until = 0.0
        self._last_wp_print = -1
        self._align_since = None
        self._align_yaw = None
        self.pick_i = 0
        self.pick_name = None
        self._creeps = 0
        self._creep_until = 0.0
        self._item_start = None
        self.vacuum = None
        self._bind_sensors()
        self._bind_arms()
        self.vacuum = self._device("palm vacuum")
        if self.vacuum is not None:
            self.vacuum.enablePresence(self.timestep)
            self.vacuum.turnOff()
        self.slide = self._device("suction slide")
        self.slide_sensor = self._device("suction slide sensor")
        if self.slide is not None:
            self.slide.setVelocity(0.08)
            self.slide.setPosition(0.0)
        if self.slide_sensor is not None:
            self.slide_sensor.enable(self.timestep)
        self.palm_range = self._device("palm range")
        if self.palm_range is not None:
            self.palm_range.enable(self.timestep)
        self.tray_well = self._device("tray well")
        if self.tray_well is not None:
            self.tray_well.enable(self.timestep)
        self._reach_j1 = REACH_RIGHT[0]
        self._reach_j2 = REACH_RIGHT[1]
        self._reach_j4 = REACH_RIGHT[3]
        self._reach_j6 = REACH_RIGHT[5]
        self._servo_sign = {"j1": 1.0, "j2": 1.0, "j4": 1.0, "j6": 1.0}
        self._servo_last = None
        self._servo_dist = None
        self._vacuum_on = False
        self._grasp_tries = 0
        self._arm_adjust_at = 0.0
        self._seek_until = 0.0
        self.apply_pose(IDLE_POSE)
        self.set_hands(closed=False)
        if not self.teleop and not self.parked:
            self.start_job()
        print(
            "ButlerServe '%s': J job, T teleop, arrows/WASD drive, Q stop."
            % self.name
        )

    def _device(self, name):
        try:
            return self.robot.getDevice(name)
        except Exception:
            return None

    def _bind_sensors(self):
        period = self.timestep
        self.lidar = self._device("Hokuyo URG-04LX-UG01")
        self.gps = self._device("gps")
        self.compass = self._device("compass")
        self.imu = self._device("inertial unit")
        self.gyro = self._device("gyro")
        self.accel = self._device("accelerometer")
        self.bumper = self._device("base_cover_link")
        self.camera_rgb = self._device("Astra rgb")
        self.camera_depth = self._device("Astra depth")
        self.sonars = []
        for name in (
            "base_sonar_front_left",
            "base_sonar_front_center",
            "base_sonar_front_right",
            "base_sonar_01_link",
            "base_sonar_02_link",
            "base_sonar_03_link",
        ):
            sonar = self._device(name)
            if sonar is not None:
                sonar.enable(period)
                self.sonars.append(sonar)
        if self.lidar is not None:
            self.lidar.enable(period * 2)
        if self.gps is not None:
            self.gps.enable(period)
        if self.compass is not None:
            self.compass.enable(period)
        if self.imu is not None:
            self.imu.enable(period)
        if self.gyro is not None:
            self.gyro.enable(period)
        if self.accel is not None:
            self.accel.enable(period)
        if self.bumper is not None:
            self.bumper.enable(period)
        if self.camera_rgb is not None:
            self.camera_rgb.enable(period * 8)
        if self.camera_depth is not None:
            self.camera_depth.enable(period * 8)

    def _bind_arms(self):
        self.arm_motors = {}
        names = list(IDLE_POSE.keys())
        for name in names:
            motor = self._device(name)
            if motor is None:
                continue
            self._limit_motor(motor, 0.75)
            self.arm_motors[name] = motor
        self.hand_flex = []
        self.hand_abd = []
        self.hand_virtual = []
        count = self.robot.getNumberOfDevices()
        for i in range(count):
            device = self.robot.getDeviceByIndex(i)
            name = device.getName()
            if not name.startswith("hand_") or not name.endswith("_joint"):
                continue
            if "sensor" in name:
                continue
            self._limit_motor(device, 0.5)
            if "virtual" in name:
                self.hand_virtual.append(device)
            elif "thumb_abd" in name:
                self.hand_abd.append(device)
            elif "flex" in name:
                self.hand_flex.append(device)

    def _limit_motor(self, motor, fraction):
        vmax = motor.getMaxVelocity()
        motor.setVelocity(max(0.0, min(vmax, vmax * fraction)))

    def apply_pose(self, pose, hold_s=0.0):
        for name, position in pose.items():
            motor = self.arm_motors.get(name)
            if motor is not None:
                motor.setPosition(position)
        if hold_s > 0.0:
            self.pose_hold_until = self.robot.getTime() + hold_s

    def set_hands(self, closed):
        flex = 0.78 if closed else 0.0
        abd = 1.45 if closed else 0.0
        for motor in self.hand_flex:
            motor.setPosition(flex)
        for motor in self.hand_abd:
            motor.setPosition(abd)
        for motor in self.hand_virtual:
            motor.setPosition(0.0)

    def posing(self):
        return self.robot.getTime() < self.pose_hold_until

    def set_wheel_speeds(self, left_rad_s, right_rad_s):
        cap = FAST_SPEED
        self.left.setVelocity(max(-cap, min(cap, left_rad_s)))
        self.right.setVelocity(max(-cap, min(cap, right_rad_s)))

    def set_base_velocity(self, linear_m_s, angular_rad_s):
        left = (linear_m_s - angular_rad_s * WHEEL_SEP / 2.0) / WHEEL_RADIUS
        right = (linear_m_s + angular_rad_s * WHEEL_SEP / 2.0) / WHEEL_RADIUS
        self.set_wheel_speeds(left, right)

    def get_pose(self):
        node = self.robot.getSelf()
        if node is not None:
            pos = node.getPosition()
            yaw = math.atan2(node.getOrientation()[3], node.getOrientation()[0])
            return pos[0], pos[1], pos[2], yaw
        if self.gps is not None:
            values = self.gps.getValues()
            yaw = 0.0
            if self.compass is not None:
                north = self.compass.getValues()
                yaw = math.atan2(north[0], north[1])
            return values[0], values[1], values[2], yaw
        return 0.0, 0.0, 0.0, 0.0

    def _goal_bearing(self, dx, dy, yaw):
        """Goal direction in the robot frame: 0 = ahead, + = left."""
        c, s = math.cos(yaw), math.sin(yaw)
        forward = dx * c + dy * s
        left = -dx * s + dy * c
        return math.atan2(left, forward), forward

    def _scan(self):
        """Lidar hits as (angle_robot_frame, range). Angle 0 is forward, + is left."""
        samples = []
        if self.lidar is None:
            return samples
        ranges = self.lidar.getRangeImage()
        if not ranges:
            return samples
        fov = self.lidar.getFov()
        max_range = self.lidar.getMaxRange()
        min_range = self.lidar.getMinRange()
        n = len(ranges)
        denom = max(n - 1, 1)
        for i, raw in enumerate(ranges):
            rng = max_range if raw is None or math.isinf(raw) or math.isnan(raw) else float(raw)
            rng = max(min_range, min(max_range, rng))
            angle = fov / 2.0 - i * fov / denom
            samples.append((angle, rng))
        return samples

    def _lidar_sectors(self):
        """Five Hokuyo sectors, same layout idea as tiago_base.c."""
        buckets = {
            "left": [],
            "front_left": [],
            "front": [],
            "front_right": [],
            "right": [],
        }
        for angle, rng in self._scan():
            if 0.70 <= angle <= 1.45:
                buckets["left"].append(rng)
            elif 0.25 <= angle < 0.70:
                buckets["front_left"].append(rng)
            elif -0.25 < angle < 0.25:
                buckets["front"].append(rng)
            elif -0.70 < angle <= -0.25:
                buckets["front_right"].append(rng)
            elif -1.45 <= angle <= -0.70:
                buckets["right"].append(rng)
        return {name: min(hits) if hits else 5.0 for name, hits in buckets.items()}

    def follow_waypoints(self):
        """Turn in place at a corner, then drive that leg in a straight line."""
        if self.wp_index >= len(self.waypoints):
            self.set_base_velocity(0.0, 0.0)
            return True
        x, y, _, yaw = self.get_pose()
        last = self.wp_index == len(self.waypoints) - 1
        tx, ty = self.waypoints[self.wp_index][0], self.waypoints[self.wp_index][1]
        dx, dy = tx - x, ty - y
        dist = math.hypot(dx, dy)
        tol = GOAL_TOL if last else WAYPOINT_TOL
        sectors = self._lidar_sectors()
        front = sectors["front"]
        bearing, forward = self._goal_bearing(dx, dy, yaw)
        arrived = dist < tol
        if last and front < 0.40 and dist < 0.95 and abs(bearing) < 0.5:
            arrived = True
        if arrived:
            if self._last_wp_print != self.wp_index:
                print("nav reached %d/%d (%.2f, %.2f)" % (
                    self.wp_index + 1, len(self.waypoints), tx, ty
                ))
                self._last_wp_print = self.wp_index
            self.wp_index += 1
            self._stuck_since = None
            self._align_since = None
            self.set_base_velocity(0.0, 0.0)
            return self.wp_index >= len(self.waypoints)
        now = self.robot.getTime()
        aligning = forward < 0.05 or abs(bearing) > HEADING_ALIGN
        behind = forward < -0.2 and abs(abs(bearing) - math.pi) < 0.9
        if behind:
            self._align_since = None
            self._stuck_since = now
            self.set_base_velocity(-0.30, 0.35 * bearing)
            return False
        if now < self._recover_until:
            self.set_base_velocity(-0.12, 0.0)
            return False
        if aligning:
            self._stuck_since = now
            self._stuck_pose = (x, y)
            turned = self._align_yaw is None or abs((yaw - self._align_yaw + math.pi) % (2.0 * math.pi) - math.pi) > 0.2
            if turned:
                self._align_yaw = yaw
                self._align_since = now
            elif self._align_since is not None and now - self._align_since > 1.6:
                print("nav turn blocked, backing up")
                self._recover_until = now + 0.7
                self._align_since = now
                self.set_base_velocity(-0.22, 0.0)
                return False
        elif self._stuck_pose is None:
            self._stuck_pose = (x, y)
            self._stuck_since = now
        elif math.hypot(x - self._stuck_pose[0], y - self._stuck_pose[1]) > 0.12:
            self._stuck_pose = (x, y)
            self._stuck_since = now
        elif self._stuck_since is not None and now - self._stuck_since > STUCK_TIME:
            print("nav stuck, reversing")
            self._recover_until = now + 0.45
            self._stuck_since = now
            self.set_base_velocity(-0.12, 0.0)
            return False
        if self.bumper is not None and self.bumper.getValue() > 0.5:
            self._recover_until = now + 0.4
            self.set_base_velocity(-0.12, 0.0)
            return False
        if aligning:
            self.set_base_velocity(0.0, math.copysign(TURN_IN_PLACE, bearing if bearing != 0.0 else 1.0))
            return False
        linear = CRUISE if dist > 0.8 else max(0.16, CRUISE * dist / 0.8)
        if last:
            linear = min(linear, 0.22)
        if not last and front < 0.55:
            linear *= max(0.4, (front - FRONT_STOP) / (0.55 - FRONT_STOP))
        self.set_base_velocity(linear, 1.1 * bearing)
        return False

    def robot_to_world(self, lx, ly, lz):
        x, y, z, yaw = self.get_pose()
        c, s = math.cos(yaw), math.sin(yaw)
        return [x + lx * c - ly * s, y + lx * s + ly * c, z + lz]

    def _vacuum(self, on):
        if self.vacuum is None:
            return
        self._vacuum_on = bool(on)
        if on:
            self.vacuum.turnOn()
        else:
            self.vacuum.turnOff()

    def _slide_pos(self):
        if self.slide_sensor is None:
            return 0.0
        value = self.slide_sensor.getValue()
        if value is None or math.isnan(value):
            return 0.0
        return float(value)

    def _set_slide(self, position):
        if self.slide is None:
            return
        self.slide.setPosition(max(0.0, min(0.22, position)))

    def _remember_item(self):
        node = self.robot.getFromDef(self.pick_name) if self.pick_name else None
        if node is None:
            self._item_start = None
            return
        pos = node.getPosition()
        self._item_start = (pos[0], pos[1], pos[2])

    def _item_carried(self):
        """True once the palm suction has actually moved this item off its rest pose."""
        node = self.robot.getFromDef(self.pick_name) if self.pick_name else None
        if node is None or self._item_start is None:
            return False
        pos = node.getPosition()
        shifted = math.hypot(pos[0] - self._item_start[0], pos[1] - self._item_start[1])
        return shifted > 0.06 or pos[2] > self._item_start[2] + 0.03

    def _node_pos(self, def_name):
        node = self.robot.getFromDef(def_name) if def_name else None
        if node is None:
            return None
        pos = node.getPosition()
        return (pos[0], pos[1], pos[2])

    def _palm_gap(self):
        """Item position minus the suction pad. None if either node is missing."""
        palm = None
        raw = getattr(self.vacuum, "_tag", None) if self.vacuum is not None else None
        try:
            tag = int(raw) if raw is not None else 0
        except (TypeError, ValueError):
            tag = 0
        if tag > 0:
            try:
                node = self.robot.getFromDevice(tag)
            except (TypeError, ctypes.ArgumentError):
                node = None
            if node is not None:
                pos = node.getPosition()
                palm = (pos[0], pos[1], pos[2])
        item = self._node_pos(self.pick_name)
        if palm is None or item is None:
            return None
        dx, dy, dz = item[0] - palm[0], item[1] - palm[1], item[2] - palm[2]
        return dx, dy, dz, math.sqrt(dx * dx + dy * dy + dz * dz)

    def _palm_range_m(self):
        if self.palm_range is None:
            return None
        value = self.palm_range.getValue()
        if value is None or math.isnan(value):
            return None
        return float(value)

    def _apply_reach(self):
        joints = (
            self._reach_j1,
            self._reach_j2,
            REACH_RIGHT[2],
            self._reach_j4,
            REACH_RIGHT[4],
            self._reach_j6,
            REACH_RIGHT[6],
        )
        self.apply_pose(_right_pose(joints, head=0.35, torso=0.26))

    def _begin_approach(self):
        name = PICKS[self.pick_i][0]
        self.pick_name = name
        self._creeps = 0
        node = self.robot.getFromDef(name)
        if node is not None:
            pos = node.getPosition()
            # Park north of the pedestal. The right arm reaches south to the box.
            if name == "PIZZA_BOX":
                x, y = pos[0] - 0.05, pos[1] + 0.80
            else:
                x, y = pos[0] - 0.95, pos[1]
        else:
            x, y = PICKS[self.pick_i][1], PICKS[self.pick_i][2]
        self._servo_sign = {"j1": 1.0, "j2": 1.0, "j4": 1.0, "j6": 1.0}
        self._servo_last = None
        self._servo_dist = None
        self._grasp_tries = 0
        self.waypoints = [(x, y, False)]
        self.wp_index = 0
        self._reset_nav()
        self.job = "approach"
        self.apply_pose(IDLE_POSE)
        self.set_hands(closed=False)
        self._vacuum(False)
        print("approach %s" % name)

    def _tray_point(self):
        """Deck point for the box, from the GPS on the tray well."""
        if self.tray_well is not None:
            vals = self.tray_well.getValues()
            if vals is not None and not any(math.isnan(v) for v in vals[:3]):
                return (vals[0], vals[1], vals[2])
        if self.pick_name in WELLS:
            return tuple(self.robot_to_world(*WELLS[self.pick_name]))
        return None

    def _tick_carry(self):
        """Hold suction and move the box until it hangs just above the tray.

        Same order as the vacuum-gripper sample and p-rob3: carry while the
        gripper is closed, then release at the place pose and pull the arm away.
        """
        now = self.robot.getTime()
        self._vacuum(True)
        self.set_hands(closed=True)
        self.set_base_velocity(0.0, 0.0)
        well = self._tray_point()
        item = self._node_pos(self.pick_name)
        if well is None or item is None:
            if now > self._seek_until:
                print("place miss %s" % self.pick_name)
                self._vacuum(False)
                self._next_item_or_deliver()
            return
        hover = (well[0], well[1], well[2] + 0.07)
        dx, dy, dz = hover[0] - item[0], hover[1] - item[1], hover[2] - item[2]
        dist = math.sqrt(dx * dx + dy * dy + dz * dz)
        horiz = math.hypot(dx, dy)
        _, _, _, yaw = self.get_pose()
        c, s = math.cos(yaw), math.sin(yaw)
        forward = dx * c + dy * s
        left = -dx * s + dy * c
        if horiz < 0.05 and abs(dz) < 0.03:
            print("release %s over tray" % self.pick_name)
            self._vacuum(False)
            self._set_slide(0.0)
            self.set_hands(closed=False)
            self._reach_j4 = min(2.0, self._reach_j4 + 0.5)
            self._reach_j2 = min(1.2, self._reach_j2 + 0.35)
            self._apply_reach()
            self.job = "settle"
            self.pose_hold_until = now + 1.2
            return
        if now > self._seek_until:
            print("place miss %s gap %.2fm" % (self.pick_name, dist))
            self._vacuum(False)
            self._next_item_or_deliver()
            return
        if now < self._arm_adjust_at:
            return
        self._servo_arm(forward, left, dz, dist)
        self._arm_adjust_at = now + 0.22

    def _tick_settle(self):
        """The box has been released. Count it only if it landed on the deck."""
        well = self._tray_point()
        item = self._node_pos(self.pick_name)
        landed = False
        if well is not None and item is not None:
            horiz = math.hypot(item[0] - well[0], item[1] - well[1])
            landed = horiz < 0.12 and well[2] - 0.05 < item[2] < well[2] + 0.05
        if landed:
            if self.pick_name not in self.carried:
                self.carried.append(self.pick_name)
            print("placed %s on tray" % self.pick_name)
        else:
            print("place miss %s" % self.pick_name)
        self._next_item_or_deliver()

    def _next_item_or_deliver(self):
        self.pick_i += 1
        if self.pick_i < len(PICKS):
            self._begin_approach()
            return
        self.job = "fold_carry"
        self.apply_pose(IDLE_POSE, hold_s=2.2)
        self.set_hands(closed=False)
        self._vacuum(False)
        self.event = "pickup"
        self.publish()
        print("pickup t=%.1f items=%s" % (self.robot.getTime(), self.carried))

    def place_on_desk(self):
        for def_name in list(self.carried):
            node = self.robot.getFromDef(def_name)
            if node is None:
                continue
            pose = PLACE_POSES[def_name]
            locked = node.getField("locked")
            if locked is not None:
                locked.setSFBool(False)
            node.getField("translation").setSFVec3f(list(pose))
            node.getField("rotation").setSFRotation([0, 0, 1, 0])
            if locked is not None:
                locked.setSFBool(True)
            node.resetPhysics()
        self.carried = []
        self.event = "delivery"
        self.publish()
        print("delivery t=%.1f room-1204" % self.robot.getTime())

    def start_job(self):
        self.teleop = False
        self.carried = []
        self.pick_i = 0
        self.event = "job"
        self._begin_approach()
        print("job start: kitchen pickup -> room-1204")

    def _reset_nav(self):
        self._stuck_since = None
        self._stuck_pose = None
        self._recover_until = 0.0
        self._last_wp_print = -1
        self._align_since = None
        self._align_yaw = None

    def _held(self):
        present = self.vacuum is not None and bool(self.vacuum.getPresence())
        return present or (self._vacuum_on and self._item_carried())

    def _servo_arm(self, forward, left, dz, dist):
        """Step one joint. If that step opened the gap, the next step reverses it."""
        if self._servo_last is not None and self._servo_dist is not None:
            if dist > self._servo_dist + 0.01:
                self._servo_sign[self._servo_last] *= -1.0
        elbow_stuck = (
            self._servo_last == "j4"
            and self._servo_dist is not None
            and dist > self._servo_dist - 0.008
        )
        # Aim the shoulder while the hand is beside the target. Stretching the
        # elbow first left it at the joint stop with the hand still behind the body.
        if abs(left) > 0.10 or elbow_stuck:
            name = "j1"
            step = -0.12 if left > 0 else 0.12
        elif forward > 0.06:
            name = "j4"
            step = -0.12
        elif forward < -0.06:
            name = "j4"
            step = 0.12
        elif abs(left) >= abs(dz) and abs(left) > 0.02:
            name = "j1"
            step = -0.10 if left > 0 else 0.10
        elif abs(dz) > 0.02:
            name = "j2"
            step = 0.10 if dz < 0 else -0.10
        else:
            name = "j6"
            step = 0.12
        step *= self._servo_sign[name]
        if dist < 0.12:
            step *= 0.55
        limits = {
            "j1": (-1.08, 1.45),
            "j2": (-1.05, 1.35),
            "j4": (-0.32, 2.1),
            "j6": (-1.3, 1.3),
        }
        attr = {"j1": "_reach_j1", "j2": "_reach_j2", "j4": "_reach_j4", "j6": "_reach_j6"}
        lo, hi = limits[name]
        cur = getattr(self, attr[name])
        nxt = min(hi, max(lo, cur + step))
        if abs(nxt - cur) < 1e-4:
            self._servo_sign[name] *= -1.0
        setattr(self, attr[name], nxt)
        self._servo_last = name
        self._servo_dist = dist
        self._apply_reach()
        print(
            "reach %s %+.2f gap %.2f (fwd %.2f left %.2f up %.2f)"
            % (name, nxt, dist, forward, left, dz)
        )

    def _tick_seek(self):
        """Keep the pad moving until suction holds the box.

        The vacuum-gripper sample does not stop when the pad is merely close.
        It stays on and keeps moving until getPresence() is true.
        """
        now = self.robot.getTime()
        gap = self._palm_gap()
        if self._held():
            self.set_base_velocity(0.0, 0.0)
            self.set_hands(closed=True)
            self._vacuum(True)
            self._set_slide(self._slide_pos())
            self.job = "grasp"
            self.pose_hold_until = now + 0.45
            print("palm on %s" % self.pick_name)
            return
        if now > self._seek_until:
            self.set_base_velocity(0.0, 0.0)
            mx, my, _, _ = self.get_pose()
            dist = gap[3] if gap else -1.0
            print("grasp miss %s at (%.2f, %.2f) palm %.2fm" % (self.pick_name, mx, my, dist))
            self._vacuum(False)
            self._next_item_or_deliver()
            return
        if gap is None:
            front = self._lidar_sectors()["front"]
            self.set_base_velocity(0.05 if front > 0.30 else 0.0, 0.0)
            return
        dx, dy, dz, dist = gap
        _, _, _, yaw = self.get_pose()
        c, s = math.cos(yaw), math.sin(yaw)
        forward = dx * c + dy * s
        left = -dx * s + dy * c
        front = self._lidar_sectors()["front"]
        # The slide is the vacuum-gripper sample's straight approach. Extend it
        # while the pizza is still ahead of the pad, and turn suction on before contact.
        slide = self._slide_pos()
        if forward > 0.02 or dist < 0.28:
            self._set_slide(slide + 0.012)
        elif forward < -0.05:
            self._set_slide(slide - 0.012)
        if dist < 0.22 or slide > 0.03:
            self._vacuum(True)
            self.set_hands(closed=True)
        lin = 0.0
        # The pedestal pickup keeps the base parked. Creeping forward puts the
        # chest and the arms into the post.
        if self.pick_name != "PIZZA_BOX" and dist > 0.06 and forward > 0.04 and front > 0.24:
            lin = 0.05
        elif forward < -0.06:
            lin = -0.04
        self.set_base_velocity(lin, 0.0)
        if now < self._arm_adjust_at:
            return
        self._servo_arm(forward, left, dz, dist)
        self._arm_adjust_at = now + 0.22

    def tick_job(self):
        if self.job is None or self.posing():
            self.set_base_velocity(0.0, 0.0)
            return
        if self.job == "approach":
            self.apply_pose(IDLE_POSE)
            x, y, _, yaw = self.get_pose()
            tx, ty = self.waypoints[0][0], self.waypoints[0][1]
            dx, dy = tx - x, ty - y
            dist = math.hypot(dx, dy)
            bearing, _forward = self._goal_bearing(dx, dy, yaw)
            if dist < 0.14:
                self.set_base_velocity(0.0, 0.0)
                where = "pizza pedestal" if self.pick_name == "PIZZA_BOX" else "counter"
                print("at %s (%.2f, %.2f) for %s" % (where, x, y, self.pick_name))
                self._reach_j1 = REACH_RIGHT[0]
                self._reach_j2 = REACH_RIGHT[1]
                self._reach_j4 = REACH_RIGHT[3]
                self._reach_j6 = REACH_RIGHT[5]
                self.job = "reach"
                self._apply_reach()
                self.pose_hold_until = self.robot.getTime() + 2.0
                self.set_hands(closed=False)
                self._vacuum(False)
            elif abs(bearing) > HEADING_ALIGN:
                self.set_base_velocity(0.0, math.copysign(TURN_IN_PLACE, bearing or 1.0))
            else:
                self.set_base_velocity(min(0.35, max(0.12, dist)), 1.0 * bearing)
        elif self.job == "reach":
            self._remember_item()
            self._seek_until = self.robot.getTime() + 14.0
            self._arm_adjust_at = self.robot.getTime() + 0.4
            self.job = "seek"
            self._vacuum(False)
            self._set_slide(0.0)
            self.set_hands(closed=False)
        elif self.job == "seek":
            self._tick_seek()
        elif self.job == "grasp":
            touched = self._item_carried()
            if self.vacuum is not None and self.vacuum.getPresence():
                touched = True
            if touched:
                print("grasped %s" % self.pick_name)
                self._vacuum(True)
                self._servo_sign = {"j1": 1.0, "j2": 1.0, "j4": 1.0, "j6": 1.0}
                self._servo_last = None
                self._servo_dist = None
                self.job = "carry"
                self._seek_until = self.robot.getTime() + 12.0
                self._arm_adjust_at = self.robot.getTime() + 0.3
            else:
                self._grasp_tries += 1
                if self._grasp_tries < 3:
                    print("suction retry %d" % self._grasp_tries)
                    self._vacuum(False)
                    self.job = "seek"
                    self._seek_until = self.robot.getTime() + 6.0
                    self._arm_adjust_at = self.robot.getTime() + 0.2
                else:
                    mx, my, _, _ = self.get_pose()
                    gap = self._palm_gap()
                    dist = gap[3] if gap else -1.0
                    print("grasp miss %s at (%.2f, %.2f) palm %.2fm" % (self.pick_name, mx, my, dist))
                    self._vacuum(False)
                    self._next_item_or_deliver()
        elif self.job == "carry":
            self._tick_carry()
        elif self.job == "settle":
            self._tick_settle()
        elif self.job == "fold_carry":
            self.waypoints = list(PATH_DELIVER)
            self.wp_index = 0
            self._reset_nav()
            self.job = "nav_deliver"
            self.event = "carrying"
        elif self.job == "nav_deliver":
            if self.follow_waypoints():
                self.job = "reach_place"
                self.apply_pose(_right_pose(TRAY_RIGHT, head=-0.2), hold_s=1.6)
                self.set_hands(closed=True)
        elif self.job == "reach_place":
            self.place_on_desk()
            self.set_hands(closed=False)
            self.job = "fold_done"
            self.apply_pose(IDLE_POSE, hold_s=2.0)
        elif self.job == "fold_done":
            self.waypoints = list(PATH_DOCK)
            self.wp_index = 0
            self._reset_nav()
            self.job = "nav_dock"
            self.event = "returning"
        elif self.job == "nav_dock":
            if self.follow_waypoints():
                self.job = None
                self.event = "idle"
                self.apply_pose(IDLE_POSE)
                self.set_base_velocity(0.0, 0.0)
                print("job complete: back at dock")

    def publish(self):
        x, y, z, yaw = self.get_pose()
        payload = {
            "name": self.name,
            "pose": [round(x, 3), round(y, 3), round(z, 3), round(yaw, 3)],
            "battery": round(self.battery, 3),
            "event": self.event,
            "carried": list(self.carried),
        }
        self.robot.setCustomData(json.dumps(payload, separators=(",", ":")))

    def _normalize_key(self, raw):
        if ord("A") <= raw <= ord("Z"):
            return raw + 32
        return raw

    def read_drive_command(self):
        speed = MAX_SPEED
        linear = 0.0
        angular = 0.0
        override = False
        held = set()
        key = self.keyboard.getKey()
        while key != -1:
            if key & SHIFT:
                speed = FAST_SPEED
            raw = self._normalize_key(key & ~CTRL_MASK)
            held.add(raw)
            if raw in (Keyboard.UP, ord("w")):
                linear += speed * WHEEL_RADIUS
                override = True
            elif raw in (Keyboard.DOWN, ord("s")):
                linear -= speed * WHEEL_RADIUS
                override = True
            elif raw in (Keyboard.LEFT, ord("a")):
                angular += speed * WHEEL_RADIUS / (WHEEL_SEP / 2.0)
                override = True
            elif raw in (Keyboard.RIGHT, ord("d")):
                angular -= speed * WHEEL_RADIUS / (WHEEL_SEP / 2.0)
                override = True
            key = self.keyboard.getKey()
        pressed = held - self._keys_held
        self._keys_held = held
        if ord("q") in pressed:
            linear = 0.0
            angular = 0.0
            override = True
            self.job = None
            print("stop")
        if ord("g") in pressed:
            x, y, z, yaw = self.get_pose()
            print(
                "pose t=%.2f name=%s x=%.2f y=%.2f yaw=%.2f battery=%.2f"
                % (self.robot.getTime(), self.name, x, y, yaw, self.battery)
            )
        if ord("t") in pressed:
            self.teleop = not self.teleop
            if self.teleop:
                self.job = None
                self.apply_pose(IDLE_POSE)
                print("teleop")
            else:
                print("autonomous (J to run job)")
        if ord("j") in pressed:
            self.start_job()
        return linear, angular, override

    def run(self):
        steps = 0
        while self.robot.step(self.timestep) != -1:
            self.battery = max(0.05, self.battery - 0.000012)
            linear, angular, override = self.read_drive_command()
            if self.parked:
                self.set_wheel_speeds(0.0, 0.0)
                self.apply_pose(IDLE_POSE)
                continue
            if override or self.teleop:
                if override:
                    self.set_base_velocity(linear, angular)
                elif self.teleop:
                    self.set_base_velocity(0.0, 0.0)
            else:
                self.tick_job()
            steps += 1
            if steps % 16 == 0:
                self.publish()


def main():
    ButlerServeController().run()


if __name__ == "__main__":
    main()
