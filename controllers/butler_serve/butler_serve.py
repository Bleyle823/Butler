"""ButlerServe: sensors, chest tray, autonomous wait-for-staff then delivery.

Webots never talks to peaq or Circle. This process publishes pose, battery,
pickup, and delivery on the robot customData field and accepts a job through
controllerArgs: autonomous (default), teleop, parked.

Select servebot-1:
  arrows / WASD   drive (teleop, or hold to override)
  Q               stop
  Shift+arrows    faster
  G               print pose
  J               start / restart the room-1204 bottle job
  T               toggle teleop
"""

from __future__ import annotations

import json
import math
import os
import sys
import urllib.request

from controller import Keyboard, Supervisor

BRIDGE_URL = os.environ.get("BUTLER_BRIDGE_URL", "http://127.0.0.1:8787")
DWELL_SEC = 8.0
MAX_SPEED = 4.0
FAST_SPEED = 6.4
WHEEL_RADIUS = 0.0985
WHEEL_SEP = 0.4044
SHIFT = Keyboard.SHIFT
CTRL_MASK = Keyboard.SHIFT | Keyboard.CONTROL | Keyboard.ALT

# Head and torso only. Kitchen staff loads the tray; this robot has no arm.
IDLE_POSE = {
    "head_1_joint": 0.0,
    "head_2_joint": -0.12,
    "torso_lift_joint": 0.22,
}
_ARM_JOINTS = ()
_FINGERS = ()
_FINGER_OPEN = ()
_FINGER_CLOSE = ()

# Open drink stand at (9.18, -2.72). The robot stops south of it and waits
# while kitchen staff places the pizza and drink on the chest tray.
COUNTER_STANCE = (8.98, -3.18)
COUNTER_YAW = math.pi / 2.0
LOAD_ITEMS = ("PIZZA_BOX", "DRINK_BOTTLE")
PICKS = (
    ("DRINK_BOTTLE", 8.98, -3.18),
)


def _arm_pose(head=0.05, torso=0.26):
    pose = dict(IDLE_POSE)
    pose["head_2_joint"] = head
    pose["torso_lift_joint"] = torso
    return pose


_GRASP_UP = 0.07
_CARRY_OFFSET = (0.0, 0.0, -0.08)
ARM_SPEED = 0.5


# Robot-frame well offsets (metres) relative to the base origin.
WELLS = {
    "PIZZA_BOX": (0.36, 0.02, 0.81),
    "DRINK_BOTTLE": (0.30, -0.10, 0.79),
    "COUNTER_PLATE": (0.34, 0.08, 0.83),
    "COUNTER_GLASS": (0.30, 0.12, 0.86),
}

PLACE_POSES = {
    "DRINK_BOTTLE": (-4.9, 3.05, 0.78),
    "PIZZA_BOX": (-5.2, 3.2, 0.76),
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
# Reverse out of 1204 through the door, then the lobby corridor to the dock.
PATH_DOCK = (
    (-6.20,  2.20, False),
    (-7.20,  2.15, True),
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
        self.vacuum = None
        self.slide = None
        self.slide_sensor = None
        self.palm_range = None
        self.tray_well = self._device("tray well")
        if self.tray_well is not None:
            self.tray_well.enable(self.timestep)
        self.tray_contact = self._device("tray_contact")
        if self.tray_contact is not None:
            self.tray_contact.enable(self.timestep)
        self._seen_goal = None
        self._dwell_until = 0.0
        # ButlerServe has no Battery node. Enabling the sensor makes Webots
        # return -1, and the controller then re-enables it on every step.
        self._battery_sensor = False
        self.picker_tool = None
        self.picker_camera = None
        self._ur = {name: IDLE_POSE[name] for name in _ARM_JOINTS}
        self._ik_bias = (0.0, 0.0, 0.0)
        self._tool_goal = None
        self._stage = 0
        self._stage_sent = False
        self._arm_q = [IDLE_POSE[name] for name in _ARM_JOINTS]
        self._arm_out = False
        self._pick_at = None
        self._grasp_local = None
        self._gripper_closed = False
        self._servo_sign = {"pan": 1.0, "lift": 1.0, "elbow": 1.0}
        self._servo_last = None
        self._servo_dist = None
        self._vacuum_on = False
        self._grasp_tries = 0
        self._arm_adjust_at = 0.0
        self._seek_until = 0.0
        self._arm_base_node = None
        self._pick_prepped = False
        self._top_arm_ready = False
        self._carry_attach = False
        self.apply_pose(IDLE_POSE)
        self.set_hands(closed=False)
        self._job_pending = not self.teleop and not self.parked
        self._last_wait_print = -1.0
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
        for name in IDLE_POSE:
            motor = self._device(name)
            if motor is None:
                continue
            if name in _ARM_JOINTS:
                motor.setVelocity(ARM_SPEED)
            else:
                self._limit_motor(motor, 0.35)
            self.arm_motors[name] = motor
        self.finger_motors = []
        for name in _FINGERS:
            motor = self._device(name)
            if motor is None:
                continue
            motor.setVelocity(0.03)
            self.finger_motors.append(motor)

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
        """Open or close the youBot two-finger gripper."""
        self._gripper_closed = bool(closed)
        if not closed:
            self._carry_attach = False
        targets = _FINGER_CLOSE if closed else _FINGER_OPEN
        for motor, position in zip(self.finger_motors, targets):
            motor.setVelocity(0.03)
            motor.setPosition(position)

    def posing(self):
        return self.robot.getTime() < self.pose_hold_until

    def set_wheel_speeds(self, left_rad_s, right_rad_s):
        cap = FAST_SPEED
        self.left.setVelocity(max(-cap, min(cap, left_rad_s)))
        self.right.setVelocity(max(-cap, min(cap, right_rad_s)))

    def set_base_velocity(self, linear_m_s, angular_rad_s):
        if math.isnan(linear_m_s) or math.isnan(angular_rad_s):
            self.set_wheel_speeds(0.0, 0.0)
            return
        left = (linear_m_s - angular_rad_s * WHEEL_SEP / 2.0) / WHEEL_RADIUS
        right = (linear_m_s + angular_rad_s * WHEEL_SEP / 2.0) / WHEEL_RADIUS
        self.set_wheel_speeds(left, right)

    def get_pose(self):
        node = self.robot.getSelf()
        if node is not None:
            pos = node.getPosition()
            rot = node.getOrientation()
            if (
                pos is not None
                and rot is not None
                and not any(math.isnan(v) for v in pos[:2])
                and not math.isnan(rot[0])
                and not math.isnan(rot[3])
            ):
                yaw = math.atan2(rot[3], rot[0])
                return pos[0], pos[1], pos[2], yaw
        if self.gps is not None:
            values = self.gps.getValues()
            if values is not None and not any(math.isnan(v) for v in values[:2]):
                yaw = 0.0
                if self.compass is not None:
                    north = self.compass.getValues()
                    if north is not None and not any(math.isnan(v) for v in north[:2]):
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

    def _world_to_robot(self, point):
        """Bottle pose in the robot base frame (same as ur5.get_bottle_frame)."""
        node = self.robot.getSelf()
        if node is None:
            return point
        pos = node.getPosition()
        rot = node.getOrientation()
        dx, dy, dz = point[0] - pos[0], point[1] - pos[1], point[2] - pos[2]
        rx = rot[0] * dx + rot[3] * dy + rot[6] * dz
        ry = rot[1] * dx + rot[4] * dy + rot[7] * dz
        rz = rot[2] * dx + rot[5] * dy + rot[8] * dz
        return (rx, ry, rz)

    def _grasp_point(self, item):
        return (item[0], item[1], item[2] + _GRASP_UP)

    def _track_bottle(self):
        """Ground-truth track (CNN-free), like ur5 predict without the model."""
        item = self._node_pos(self.pick_name)
        if item is None:
            return None
        self._pick_at = self._grasp_point(item)
        return self._pick_at

    def _palm_gap(self):
        """Item position minus the suction pad. None if either node is missing."""
        palm = None
        if self.picker_tool is not None:
            vals = self.picker_tool.getValues()
            if vals is not None and not any(math.isnan(v) for v in vals[:3]):
                palm = (vals[0], vals[1], vals[2])
        raw = getattr(self.vacuum, "_tag", None) if palm is None and self.vacuum is not None else None
        try:
            tag = int(raw) if raw is not None else 0
        except (TypeError, ValueError):
            tag = 0
        if tag > 0:
            try:
                node = self.robot.getFromDevice(tag)
            except (TypeError, ValueError):
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
        pose = _arm_pose(head=0.35, torso=0.26)
        pose.update(self._ur)
        self.apply_pose(pose)

    def _begin_approach(self):
        name = PICKS[self.pick_i][0]
        self.pick_name = name
        self._creeps = 0
        self._stage = 0
        self._stage_sent = False
        self._ik_bias = (0.0, 0.0, 0.0)
        self._tool_goal = None
        self._pick_at = None
        self._grasp_local = None
        self._pick_prepped = False
        self._top_arm_ready = False
        self._carry_attach = False
        x, y, _, _ = self.get_pose()
        sx, sy = COUNTER_STANCE
        if math.hypot(sx - x, sy - y) < 0.45 or (x == 0.0 and y == 0.0):
            self.waypoints = [(sx, -3.40, False), (sx, sy, False)]
        else:
            self.waypoints = [
                (x, -3.40, False),
                (sx, -3.40, False),
                (sx, sy, False),
            ]
        print(
            "path to %s: %s"
            % (name, ", ".join("(%.2f, %.2f)" % (px, py) for px, py, _ in self.waypoints))
        )
        self.wp_index = 0
        self._reset_nav()
        self.job = "approach"
        self.apply_pose(IDLE_POSE)
        self.set_hands(closed=False)
        print("approach %s" % name)

    def _each_scene_child(self, node):
        if node is None:
            return
        for field_name in ("children", "endPoint"):
            try:
                field = node.getField(field_name)
            except Exception:
                continue
            if field is None:
                continue
            try:
                for index in range(field.getCount()):
                    yield field.getMFNode(index)
            except Exception:
                try:
                    child = field.getSFNode()
                except Exception:
                    child = None
                if child is not None:
                    yield child

    def _find_named_node(self, node, target):
        if node is None:
            return None
        try:
            name_field = node.getField("name")
            if name_field is not None and name_field.getSFString() == target:
                return node
        except Exception:
            pass
        for child in self._each_scene_child(node):
            found = self._find_named_node(child, target)
            if found is not None:
                return found
        return None

    def _get_arm_base(self):
        if self._arm_base_node is None:
            self._arm_base_node = self._find_named_node(self.robot.getSelf(), "butler picker")
        return self._arm_base_node

    def _world_to_arm(self, point):
        """Express a world point in the live UR5 base frame (not yaw-only robot frame)."""
        base = self._get_arm_base()
        if base is None:
            x, y, z, yaw = self.get_pose()
            torso = 0.26
            ox, oz = 0.05, 0.274 + 0.6 + torso
            c, s = math.cos(yaw), math.sin(yaw)
            ax, ay = x + ox * c, y + ox * s
            az = z + oz
            dx, dy, dz = point[0] - ax, point[1] - ay, point[2] - az
            return (dx * c + dy * s, -dx * s + dy * c, dz)
        pos = base.getPosition()
        rot = base.getOrientation()
        dx, dy, dz = point[0] - pos[0], point[1] - pos[1], point[2] - pos[2]
        lx = rot[0] * dx + rot[3] * dy + rot[6] * dz
        ly = rot[1] * dx + rot[4] * dy + rot[7] * dz
        lz = rot[2] * dx + rot[5] * dy + rot[8] * dz
        return (lx, ly, lz)

    def _go_joints(self, angles, hold=True):
        """Command youBot arm joints. Hold long enough for the preset to settle."""
        torso = 0.28 if self.job == "pick" else 0.26
        pose = _arm_pose(head=-0.12, torso=torso)
        travel = 0.0
        for name, angle, previous in zip(_ARM_JOINTS, angles, self._arm_q):
            pose[name] = angle
            travel = max(travel, abs(angle - previous))
        self._arm_q = [pose[name] for name in _ARM_JOINTS]
        hold_s = (travel / ARM_SPEED + 1.4) if hold else 0.0
        self.apply_pose(pose, hold_s=hold_s)
        return hold_s

    def _bottle_local(self):
        """Bottle grasp in the youBot arm base frame."""
        item = self._node_pos(self.pick_name)
        if item is None:
            return None
        return self._world_to_arm((item[0], item[1], item[2] + _GRASP_UP))

    def _calibrate_tool(self):
        if self.picker_tool is None or self._tool_goal is None:
            return
        vals = self.picker_tool.getValues()
        if vals is None or any(math.isnan(v) for v in vals[:3]):
            return
        bias = tuple(max(-0.08, min(0.08, self._tool_goal[i] - vals[i])) for i in range(3))
        self._ik_bias = bias

    def _tool_near_goal(self, tol=0.07):
        if self._tool_goal is None or self.picker_tool is None:
            return True
        vals = self.picker_tool.getValues()
        if vals is None or any(math.isnan(v) for v in vals[:3]):
            return True
        gap = math.sqrt(sum((vals[i] - self._tool_goal[i]) ** 2 for i in range(3)))
        return gap <= tol

    def _tool_gap_to_grasp(self):
        if self._pick_at is None or self.picker_tool is None:
            return None
        vals = self.picker_tool.getValues()
        if vals is None or any(math.isnan(v) for v in vals[:3]):
            return None
        return math.sqrt(sum((vals[i] - self._pick_at[i]) ** 2 for i in range(3)))

    def _sync_carried_to_tool(self):
        if not self._carry_attach or self.pick_name is None:
            return
        node = self.robot.getFromDef(self.pick_name)
        if node is None or self.picker_tool is None:
            return
        vals = self.picker_tool.getValues()
        if vals is None or any(math.isnan(v) for v in vals[:3]):
            return
        ox, oy, oz = _CARRY_OFFSET
        node.getField("translation").setSFVec3f(
            [vals[0] + ox, vals[1] + oy, vals[2] + oz]
        )
        node.resetPhysics()

    def _item_on_tray(self, name):
        item = self._node_pos(name)
        if item is None:
            return False
        rx, ry, rz, yaw = self.get_pose()
        dx, dy = item[0] - rx, item[1] - ry
        c, s = math.cos(yaw), math.sin(yaw)
        forward = dx * c + dy * s
        left = -dx * s + dy * c
        return 0.10 < forward < 0.60 and abs(left) < 0.32 and item[2] > rz + 0.50

    def _tray_pressed(self):
        sensor = getattr(self, "tray_contact", None)
        if sensor is None:
            return False
        try:
            return float(sensor.getValue()) > 0.0
        except Exception:
            return False

    def _tick_wait_load(self):
        """Park at the counter until kitchen staff sets pizza and drink on the tray."""
        loaded = [name for name in LOAD_ITEMS if self._item_on_tray(name) or self._tray_pressed()]
        now = self.robot.getTime()
        if now - self._last_wait_print >= 2.0 and len(loaded) < len(LOAD_ITEMS):
            self._last_wait_print = now
            missing = [name for name in LOAD_ITEMS if name not in loaded]
            print("waiting for staff, still need %s" % missing)
        if len(loaded) < len(LOAD_ITEMS):
            return
        self.carried = list(loaded)
        self.event = "pickup"
        self.publish()
        print("pickup t=%.1f items=%s" % (self.robot.getTime(), self.carried))
        self.job = "fold_carry"

    def _seat_on_tray(self, well):
        """Set the bottle upright in the tray recess. The fingers are still closed."""
        if well is None or self.pick_name is None:
            return
        node = self.robot.getFromDef(self.pick_name)
        if node is None:
            return
        # Well GPS is 4 cm above the deck. The bottle origin is its base.
        node.getField("translation").setSFVec3f([well[0], well[1], well[2] - 0.035])
        node.getField("rotation").setSFRotation([0, 0, 1, 0])
        node.resetPhysics()

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
            self._ur = {name: IDLE_POSE[name] for name in _ARM_JOINTS}
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
            deck = well[2] - 0.035
            landed = horiz < 0.15 and abs(item[2] - deck) < 0.06
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
        print("job start: wait for staff to load pizza and drink, then room-1204")

    def _reset_nav(self):
        self._stuck_since = None
        self._stuck_pose = None
        self._recover_until = 0.0
        self._last_wp_print = -1
        self._align_since = None
        self._align_yaw = None

    def _held(self):
        if self.vacuum is not None and bool(self.vacuum.getPresence()):
            return True
        return self._gripper_closed and self._item_carried()

    def _servo_arm(self, forward, left, dz, dist):
        _ = (forward, left, dz, dist)

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
        # Close the gripper once the tool is on the box.
        if dist < 0.14:
            self.set_hands(closed=True)
        lin = 0.0
        # The pedestal pickup keeps the base parked. Creeping forward puts the
        # chest and the arms into the post.
        if self.pick_name != "DRINK_BOTTLE" and dist > 0.06 and forward > 0.04 and front > 0.24:
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
            if self.follow_waypoints():
                x, y, _, _ = self.get_pose()
                print("at counter (%.2f, %.2f), waiting for staff" % (x, y))
                self.set_base_velocity(0.0, 0.0)
                self.job = "wait_load"
                self.event = "waiting_load"
                self.publish()
            return
        elif self.job == "wait_load":
            self.set_base_velocity(0.0, 0.0)
            self._tick_wait_load()
        elif self.job == "pick":
            self.set_base_velocity(0.0, 0.0)
            self._tick_wait_load()
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
                self.job = "dwell_room"
                self._dwell_until = self.robot.getTime() + DWELL_SEC
                self.event = "at_dropoff"
                self.publish()
                self.set_base_velocity(0.0, 0.0)
        elif self.job == "dwell_room":
            self.set_base_velocity(0.0, 0.0)
            if self.robot.getTime() >= self._dwell_until:
                self.job = "reach_place"
                self.apply_pose(_arm_pose(head=-0.2), hold_s=1.6)
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

    def _read_battery(self):
        if getattr(self, "_battery_sensor", False):
            try:
                raw = float(self.robot.batterySensorGetValue())
                if 0.0 < raw <= 1.0:
                    self.battery = raw
            except Exception:
                pass
        return self.battery

    def publish(self):
        x, y, z, yaw = self.get_pose()
        payload = {
            "name": self.name,
            "pose": [round(x, 3), round(y, 3), round(z, 3), round(yaw, 3)],
            "battery": round(self._read_battery(), 3),
            "event": self.event,
            "carried": list(self.carried),
        }
        encoded = json.dumps(payload, separators=(",", ":"))
        self.robot.setCustomData(encoded)
        self._post_bridge("/telemetry", payload)

    def _post_bridge(self, path, payload):
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            BRIDGE_URL + path,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=0.2) as response:
                response.read()
        except Exception:
            return

    def _poll_goal(self):
        request = urllib.request.Request(BRIDGE_URL + "/robots/" + self.name + "/goal")
        try:
            with urllib.request.urlopen(request, timeout=0.2) as response:
                body = json.loads(response.read().decode("utf-8") or "{}")
        except Exception:
            return
        job_id = body.get("jobId")
        room = body.get("room")
        if not job_id or job_id == self._seen_goal:
            return
        if "peaq" in body or "circle" in body or "wallet" in body:
            return
        self._seen_goal = job_id
        self.dropoff_room = room
        self.start_job()

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
            if getattr(self, "_job_pending", False):
                self._job_pending = False
                self.start_job()
            if override or self.teleop:
                if override:
                    self.set_base_velocity(linear, angular)
                elif self.teleop:
                    self.set_base_velocity(0.0, 0.0)
            else:
                self.tick_job()
            if self._carry_attach:
                self._sync_carried_to_tool()
            steps += 1
            if steps % 32 == 0:
                self._poll_goal()
            if steps % 16 == 0:
                self.publish()


def main():
    ButlerServeController().run()


if __name__ == "__main__":
    main()
