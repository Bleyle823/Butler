"""ButlerServe: front arm picks up the kitchen bottle and delivers it.

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

from controller import Field, Keyboard, Supervisor

BRIDGE_URL = os.environ.get("BUTLER_BRIDGE_URL", "http://127.0.0.1:8787")
DWELL_SEC = 8.0
MAX_SPEED = 4.0
FAST_SPEED = 6.4
WHEEL_RADIUS = 0.0985
WHEEL_SEP = 0.4044
SHIFT = Keyboard.SHIFT
CTRL_MASK = Keyboard.SHIFT | Keyboard.CONTROL | Keyboard.ALT

# Front arm folded while driving. The live robot grasps ORDER_BOTTLE.
_ARM_JOINTS = (
    "arm_1_joint",
    "arm_2_joint",
    "arm_3_joint",
    "arm_4_joint",
    "arm_5_joint",
    "arm_6_joint",
    "arm_7_joint",
)
_FINGERS = ("gripper_left_finger_joint", "gripper_right_finger_joint")
_FINGER_OPEN = (0.045, 0.045)
# Open gap is about 0.098 m. The bottle body is 0.088 m across, so 0.034
# leaves the pads pressed on the bottle instead of meeting past it.
_FINGER_CLOSE = (0.034, 0.034)
# Midpoint of the two finger pads, in the wrist solid frame.
_PINCH_LOCAL = (0.190, 0.0, 0.0)
# WaterBottle body cylinder center, above the proto origin (the base).
_BODY_CENTER_Z = 0.122
ORDER_ITEM = "ORDER_BOTTLE"

FOLDED_POSE = {
    "head_1_joint": 0.0,
    "head_2_joint": -0.2,
    "torso_lift_joint": 0.15,
    "arm_1_joint": 0.15,
    "arm_2_joint": -0.9,
    "arm_3_joint": -1.6,
    "arm_4_joint": 1.7,
    "arm_5_joint": 0.2,
    "arm_6_joint": 0.4,
    "arm_7_joint": 0.0,
}
# Elbow stays back, forearm clears the table edge, fingers come down on the bottle.
REACH_POSE = {
    "head_1_joint": 0.0,
    "head_2_joint": -0.55,
    "torso_lift_joint": 0.28,
    "arm_1_joint": 0.40,
    "arm_2_joint": -0.85,
    "arm_3_joint": -1.90,
    "arm_4_joint": 2.20,
    "arm_5_joint": 0.0,
    "arm_6_joint": -1.15,
    "arm_7_joint": 1.57,
}
# Keep the grasp wrist so the fingers stay on the bottle while the base drives.
CARRY_POSE = REACH_POSE
# Same arm as the grasp. The room desk is the same height as the kitchen table,
# so this pose sets the bottle down instead of holding it at a different height.
PLACE_POSE = {
    "head_1_joint": 0.0,
    "head_2_joint": -0.55,
    "torso_lift_joint": 0.28,
    "arm_1_joint": 0.40,
    "arm_2_joint": -0.85,
    "arm_3_joint": -1.90,
    "arm_4_joint": 2.20,
    "arm_5_joint": 0.0,
    "arm_6_joint": -1.15,
    "arm_7_joint": 1.57,
}
IDLE_POSE = FOLDED_POSE

# Source kitchen: robot at the origin facing -Y, upright water bottle(2) on the
# dining table. The table is 1.0 m by 1.8 m, so the hand only reaches the short
# (east) side. Stance is that side, facing the bottle, at the measured pinch.
# Park east of the table, where the extended hand is still clear of the top,
# then creep west until the fingers meet the bottle.
COUNTER_STANCE = (8.70, -4.860)
COUNTER_YAW = math.pi
BOTTLE_HOME = (7.769, -4.806, 0.738)
LOAD_ITEMS = (ORDER_ITEM,)
PICKS = (
    (ORDER_ITEM, 8.70, -4.860),
)


def _arm_pose(head=0.05, torso=0.26):
    pose = dict(IDLE_POSE)
    pose["head_2_joint"] = head
    pose["torso_lift_joint"] = torso
    return pose


_GRASP_UP = 0.07
ARM_SPEED = 0.5


# Robot-frame well offsets (metres) relative to the base origin.
WELLS = {
    "PIZZA_BOX": (0.36, 0.02, 0.81),
    "DRINK_BOTTLE": (0.30, -0.10, 0.79),
    "COUNTER_PLATE": (0.34, 0.08, 0.83),
    "COUNTER_GLASS": (0.30, 0.12, 0.86),
}

PLACE_POSES = {
    ORDER_ITEM: (-5.45, 3.15, 0.73),
}
# Same standoff as the kitchen grasp: hand 0.66 m forward, facing the desktop.
PLACE_STANCE = (-5.382, 2.595)
PLACE_YAW = math.pi / 2.0

# Dock faces +Y. First corner is northeast of the parked row, not into the
# west-wall furniture. Then north to the lobby door latitude and through.
PATH_PICKUP = (
    (-8.40, -5.00, False),
    (-8.40, -2.10, False),
    (-7.00, -2.10, False),
    (-7.00, -0.20, False),
    ( 4.00,  0.00, False),
    ( 4.00, -1.65, True),
    ( 3.20, -3.40, False),
    ( 3.20, -5.30, False),
    ( 6.30, -5.20, False),
    ( 6.50, -3.70, False),
    ( 8.70, -3.65, False),
    ( 8.70, -4.86, False),
)
PATH_DELIVER = (
    ( 8.70, -4.86, False),
    ( 8.70, -3.70, False),
    ( 6.50, -3.70, False),
    ( 6.30, -5.20, False),
    ( 3.20, -5.30, False),
    ( 3.20, -3.40, False),
    ( 4.00, -2.20, False),
    ( 4.00,  0.00, True),
    (-7.20,  0.00, False),
    (-7.20,  2.15, True),
    (-6.20,  2.40, False),
    (-5.382, 2.595, False),
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
        self.sensor_display = self._device("display")
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
            self.lidar.enable(period * 4)
            self.lidar.enablePointCloud()
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
            self.camera_rgb.enable(period * 4)
        if self.camera_depth is not None:
            self.camera_depth.enable(period * 4)
        shown = [
            name
            for name, device in (
                ("Astra rgb", self.camera_rgb),
                ("Astra depth", self.camera_depth),
                ("Hokuyo URG-04LX-UG01", self.lidar),
                ("gps", self.gps),
                ("compass", self.compass),
                ("display", self.sensor_display),
                ("inertial unit", self.imu),
                ("gyro", self.gyro),
                ("accelerometer", self.accel),
                ("base_cover_link", self.bumper),
            )
            if device is not None
        ]
        print("sensors: %s; sonars %d" % (", ".join(shown), len(self.sonars)))

    def _bind_arms(self):
        self.arm_motors = {}
        for name in IDLE_POSE:
            motor = self._device(name)
            if motor is None:
                continue
            if name == "torso_lift_joint":
                motor.setVelocity(motor.getMaxVelocity())
            elif name in _ARM_JOINTS:
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
        """Open the jaws, or close them onto the bottle body."""
        self._gripper_closed = bool(closed)
        if not closed:
            self._carry_attach = False
        targets = _FINGER_CLOSE if closed else _FINGER_OPEN
        for motor, position in zip(self.finger_motors, targets):
            motor.setVelocity(0.05 if closed else 0.03)
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

    def _sensor_line(self, label, device):
        if device is None:
            return "%s --" % label
        try:
            if label == "imu":
                values = device.getRollPitchYaw()
            else:
                values = device.getValues()
        except Exception:
            return "%s --" % label
        if not values or len(values) < 3:
            return "%s --" % label
        return "%s %.2f %.2f %.2f" % (label, values[0], values[1], values[2])

    def _paint_sensors(self):
        """Draw the Hokuyo scan on the same 200x300 display the kitchen robot uses."""
        display = getattr(self, "sensor_display", None)
        if display is None:
            return
        width = display.getWidth()
        height = display.getHeight()
        display.setColor(0x101418)
        display.fillRectangle(0, 0, width, height)
        cx = width // 2
        cy = int(height * 0.68)
        if self.lidar is not None:
            ranges = self.lidar.getRangeImage()
            if ranges:
                fov = float(self.lidar.getFov())
                max_range = float(self.lidar.getMaxRange() or 5.6)
                scale = (min(cx, cy) - 8) / max_range
                step = max(1, len(ranges) // 160)
                display.setColor(0x7DCEA0)
                last = max(len(ranges) - 1, 1)
                for index in range(0, len(ranges), step):
                    raw = ranges[index]
                    if raw is None or math.isinf(raw) or math.isnan(raw):
                        continue
                    dist = max(0.0, min(max_range, float(raw)))
                    angle = fov / 2.0 - index * fov / last
                    px = int(cx + math.sin(angle) * dist * scale)
                    py = int(cy - math.cos(angle) * dist * scale)
                    if 0 <= px < width and 114 <= py < height:
                        display.drawPixel(px, py)
        display.setColor(0xE74C3C)
        display.fillRectangle(cx - 2, cy - 2, 4, 4)
        x, y, _, yaw = self.get_pose()
        display.setColor(0xF4F1EA)
        display.drawText("gps %.2f %.2f" % (x, y), 4, 4)
        display.drawText("yaw %.2f" % yaw, 4, 16)
        display.drawText(self._sensor_line("compass", self.compass), 4, 28)
        display.drawText(self._sensor_line("imu", self.imu), 4, 40)
        display.drawText(self._sensor_line("accel", self.accel), 4, 52)
        display.drawText(self._sensor_line("gyro", self.gyro), 4, 64)
        if self.bumper is not None:
            try:
                hit = float(self.bumper.getValue()) > 0.5
            except Exception:
                hit = False
            display.drawText("bumper %s" % ("hit" if hit else "clear"), 4, 76)
        if self.lidar is not None:
            ranges = self.lidar.getRangeImage() or []
            display.drawText("lidar %d" % len(ranges), 4, 88)
        if self.sonars:
            try:
                near = min(float(sonar.getValue()) for sonar in self.sonars)
            except Exception:
                near = -1.0
            display.drawText("sonar %d min %.2f" % (len(self.sonars), near), 4, 100)

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

    def _opening(self, sectors):
        """Front range the base should trust. A carried hand sits in the center beam."""
        front = sectors["front"]
        # The arm and a carried bottle sit in the center beam. Walls show up on the sides.
        if (self._carry_attach or self.job in ("approach", "nav_deliver")) and front < 0.55:
            return min(sectors["front_left"], sectors["front_right"])
        return front

    def _clearance_turn(self, sectors):
        """Positive turns left, away from the nearer side."""
        left = min(sectors["left"], sectors["front_left"])
        right = min(sectors["right"], sectors["front_right"])
        turn = 0.0
        if left < 0.58:
            turn -= (0.58 - left) * 2.0
        if right < 0.58:
            turn += (0.58 - right) * 2.0
        return max(-1.2, min(1.2, turn))

    def _shift_waypoint(self, sectors):
        """Nudge a blocked waypoint toward the open side so the next try clears it."""
        tx, ty, flag = self.waypoints[self.wp_index]
        x, y, _, yaw = self.get_pose()
        left = sectors["left"] + sectors["front_left"]
        right = sectors["right"] + sectors["front_right"]
        sign = 1.0 if left >= right else -1.0
        # Left of the current heading.
        ox = -math.sin(yaw) * 0.40 * sign
        oy = math.cos(yaw) * 0.40 * sign
        self.waypoints[self.wp_index] = (tx + ox, ty + oy, flag)
        print("nav shift waypoint %d toward open space" % (self.wp_index + 1))

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
        # The counter stance has to be close enough for the arm to reach the bottle.
        # Other goals stay loose so the base does not grind into a desk or the dock.
        if last and self.job == "approach":
            tol = 0.18
        else:
            tol = GOAL_TOL if last else WAYPOINT_TOL
        sectors = self._lidar_sectors()
        front = self._opening(sectors)
        bearing, forward = self._goal_bearing(dx, dy, yaw)
        arrived = dist < tol
        closing_on_counter = last and self.job == "approach" and dist < 0.50
        if (
            last
            and self.job not in ("approach", "nav_deliver")
            and front < 0.36
            and dist < 0.70
            and abs(bearing) < 0.5
        ):
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
            self.set_base_velocity(-0.16, getattr(self, "_recover_turn", 0.0))
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
                self._recover_turn = math.copysign(0.6, bearing if bearing != 0.0 else 1.0)
                self._recover_until = now + 0.7
                self._align_since = now
                self.set_base_velocity(-0.18, self._recover_turn)
                return False
        elif self._stuck_pose is None:
            self._stuck_pose = (x, y)
            self._stuck_since = now
        elif math.hypot(x - self._stuck_pose[0], y - self._stuck_pose[1]) > 0.12:
            self._stuck_pose = (x, y)
            self._stuck_since = now
        elif self._stuck_since is not None and now - self._stuck_since > STUCK_TIME:
            print("nav stuck, reversing")
            counts = getattr(self, "_stuck_counts", None)
            if counts is None:
                counts = {}
                self._stuck_counts = counts
            counts[self.wp_index] = counts.get(self.wp_index, 0) + 1
            if counts[self.wp_index] >= 2:
                self._shift_waypoint(sectors)
            side = 0.8 if sectors["left"] + sectors["front_left"] >= sectors["right"] + sectors["front_right"] else -0.8
            self._recover_turn = side
            self._recover_until = now + 0.9
            self._stuck_since = now
            self.set_base_velocity(-0.18, side)
            return False
        if self.bumper is not None and self.bumper.getValue() > 0.5:
            side = 0.7 if sectors["left"] >= sectors["right"] else -0.7
            self._recover_turn = side
            self._recover_until = now + 0.6
            self.set_base_velocity(-0.16, side)
            return False
        avoid = 0.0 if closing_on_counter else self._clearance_turn(sectors)
        if aligning:
            self.set_base_velocity(0.0, math.copysign(TURN_IN_PLACE, bearing if bearing != 0.0 else 1.0))
            return False
        if front < 0.30 and not closing_on_counter:
            open_side = max(sectors["front_left"], sectors["front_right"])
            if open_side > 0.50:
                self.set_base_velocity(0.10, avoid if abs(avoid) > 0.25 else math.copysign(0.7, avoid or 1.0))
            else:
                self.set_base_velocity(-0.08, avoid if avoid != 0.0 else 0.6)
            return False
        linear = CRUISE if dist > 0.8 else max(0.16, CRUISE * dist / 0.8)
        if last:
            linear = min(linear, 0.22)
        if not closing_on_counter and front < 0.55:
            linear *= max(0.35, (front - FRONT_STOP) / (0.55 - FRONT_STOP))
        self.set_base_velocity(linear, 1.1 * bearing + 0.55 * avoid)
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
        if math.hypot(sx - x, sy - y) < 0.45:
            self.waypoints = [(sx, sy, False)]
        elif x > 6.0 and y < -2.0:
            self.apply_pose(IDLE_POSE)
            self.waypoints = [
                (8.70, -3.65, False),
                (8.70, -4.86, False),
                (sx, sy, False),
            ]
        else:
            self.apply_pose(IDLE_POSE)
            self.waypoints = list(PATH_PICKUP)
        print(
            "path to %s: %s"
            % (name, ", ".join("(%.2f, %.2f)" % (px, py) for px, py, _ in self.waypoints))
        )
        self.wp_index = 0
        self._reset_nav()
        self.job = "approach"
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

    def _node_fields(self, node):
        try:
            if node.isProto():
                return [
                    node.getBaseNodeFieldByIndex(index)
                    for index in range(node.getNumberOfBaseNodeFields())
                ]
        except Exception:
            pass
        try:
            return [node.getFieldByIndex(index) for index in range(node.getNumberOfFields())]
        except Exception:
            return []

    def _find_named_solid(self, wanted):
        root = self.robot.getSelf()
        if root is None:
            return None

        def walk(node, depth):
            if node is None or depth > 32:
                return None
            name_field = node.getField("name")
            if name_field is not None:
                try:
                    named = name_field.getSFString() == wanted
                except Exception:
                    named = False
                if named:
                    try:
                        pos = node.getPosition()
                    except Exception:
                        pos = None
                    if pos is not None and not any(math.isnan(v) for v in pos[:3]):
                        return node
            for field in self._node_fields(node):
                try:
                    kind = field.getType()
                except Exception:
                    continue
                if kind == Field.MF_NODE:
                    for index in range(min(field.getCount(), 40)):
                        found = walk(field.getMFNode(index), depth + 1)
                        if found is not None:
                            return found
                elif kind == Field.SF_NODE:
                    found = walk(field.getSFNode(), depth + 1)
                    if found is not None:
                        return found
            return None

        return walk(root, 0)

    def _wrist_node(self):
        node = getattr(self, "_wrist_node_cached", None)
        if node is not None:
            return node
        node = self._find_named_solid("wrist_ft_tool_link")
        self._wrist_node_cached = node
        return node

    def _finger_link(self, name):
        cache = getattr(self, "_finger_links", None)
        if cache is None:
            cache = {}
            self._finger_links = cache
        if name not in cache:
            cache[name] = self._find_named_solid(name)
        return cache[name]

    def _pad_point(self, node):
        try:
            pos = node.getPosition()
            rot = node.getOrientation()
        except Exception:
            return None
        if (
            pos is None
            or rot is None
            or len(rot) != 9
            or any(math.isnan(v) for v in list(pos[:3]) + list(rot))
        ):
            return None
        lx, ly, lz = 0.004, 0.0, -0.1741
        return (
            pos[0] + rot[0] * lx + rot[1] * ly + rot[2] * lz,
            pos[1] + rot[3] * lx + rot[4] * ly + rot[5] * lz,
            pos[2] + rot[6] * lx + rot[7] * ly + rot[8] * lz,
        )

    def _gripper_world(self):
        """World point between the finger pads."""
        pads = []
        for name in ("gripper_left_finger_link", "gripper_right_finger_link"):
            node = self._finger_link(name)
            if node is None:
                pads = []
                break
            point = self._pad_point(node)
            if point is None:
                pads = []
                break
            pads.append(point)
        if len(pads) == 2:
            return tuple((pads[0][i] + pads[1][i]) / 2.0 for i in range(3))
        node = self._wrist_node()
        if node is None:
            return None
        try:
            pos = node.getPosition()
            rot = node.getOrientation()
        except Exception:
            return None
        if (
            pos is None
            or rot is None
            or len(rot) != 9
            or any(math.isnan(v) for v in list(pos[:3]) + list(rot))
        ):
            return None
        lx, ly, lz = _PINCH_LOCAL
        return (
            pos[0] + rot[0] * lx + rot[1] * ly + rot[2] * lz,
            pos[1] + rot[3] * lx + rot[4] * ly + rot[5] * lz,
            pos[2] + rot[6] * lx + rot[7] * ly + rot[8] * lz,
        )

    def _set_world(self, node, world):
        parent = node.getParentNode()
        origin = parent.getPosition() if parent is not None else (0.0, 0.0, 0.0)
        if origin is None:
            origin = (0.0, 0.0, 0.0)
        dx = world[0] - origin[0]
        dy = world[1] - origin[1]
        dz = world[2] - origin[2]
        local = [dx, dy, dz]
        if parent is not None:
            try:
                rot = parent.getOrientation()
            except Exception:
                rot = None
            if rot is not None and len(rot) == 9:
                local = [
                    rot[0] * dx + rot[3] * dy + rot[6] * dz,
                    rot[1] * dx + rot[4] * dy + rot[7] * dz,
                    rot[2] * dx + rot[5] * dy + rot[8] * dz,
                ]
        node.getField("translation").setSFVec3f(local)
        node.resetPhysics()

    def _order_bottle(self):
        node = self.robot.getFromDef(ORDER_ITEM)
        if node is None:
            return None, None
        pos = node.getPosition()
        if pos is None or any(math.isnan(v) for v in pos[:3]):
            return None, None
        return node, pos

    def _on_counter(self, pos):
        return (
            math.hypot(pos[0] - BOTTLE_HOME[0], pos[1] - BOTTLE_HOME[1]) < 0.45
            and abs(pos[2] - BOTTLE_HOME[2]) < 0.40
        )

    def _sync_carried_to_tool(self):
        if not self._carry_attach or self.pick_name is None:
            return
        node = self.robot.getFromDef(self.pick_name)
        pinch = self._gripper_world()
        if node is None or pinch is None:
            return
        self._set_world(node, (pinch[0], pinch[1], pinch[2] - _BODY_CENTER_Z))
        rotation = node.getField("rotation")
        if rotation is not None:
            rotation.setSFRotation([0, 0, 1, 0])
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

    def _open_fingers(self):
        self._gripper_closed = False
        for motor, position in zip(self.finger_motors, _FINGER_OPEN):
            motor.setVelocity(0.05)
            motor.setPosition(position)

    def _ease_onto_desk(self):
        """Lower the bottle from the open hand onto the desktop."""
        node = self.robot.getFromDef(ORDER_ITEM)
        start = getattr(self, "_release_from", None)
        if node is None or start is None:
            return True
        desk = PLACE_POSES[ORDER_ITEM]
        dx = desk[0] - start[0]
        dy = desk[1] - start[1]
        if math.hypot(dx, dy) > 0.28:
            target = (start[0], start[1], desk[2])
        else:
            target = desk
        elapsed = self.robot.getTime() - self._release_t
        blend = max(0.0, min(1.0, elapsed / 0.9))
        smooth = blend * blend * (3.0 - 2.0 * blend)
        self._set_world(
            node,
            (
                start[0] + (target[0] - start[0]) * smooth,
                start[1] + (target[1] - start[1]) * smooth,
                start[2] + (target[2] - start[2]) * smooth,
            ),
        )
        rotation = node.getField("rotation")
        if rotation is not None:
            rotation.setSFRotation([0, 0, 1, 0])
        node.resetPhysics()
        return blend >= 1.0

    def _tick_place(self):
        """Turn to the desk, lower the hand, open the fingers, set the bottle down."""
        stage = getattr(self, "_place_stage", "aim")
        now = self.robot.getTime()
        _, _, _, yaw = self.get_pose()
        err = (PLACE_YAW - yaw + math.pi) % (2.0 * math.pi) - math.pi
        if stage == "aim":
            if abs(err) > 0.15:
                self.set_base_velocity(0.0, math.copysign(0.5, err if err != 0.0 else 1.0))
                return
            self.set_base_velocity(0.0, 0.0)
            self.apply_pose(PLACE_POSE, hold_s=2.2)
            self._place_stage = "lower"
            self._place_until = now + 6.0
            return
        if stage == "lower":
            self.set_base_velocity(0.0, 0.0)
            if self.posing():
                return
            pinch = self._gripper_world()
            desk = PLACE_POSES[ORDER_ITEM]
            over = (
                pinch is not None
                and math.hypot(pinch[0] - desk[0], pinch[1] - desk[1]) < 0.22
                and pinch[2] < desk[2] + _BODY_CENTER_Z + 0.10
            )
            if over or now >= getattr(self, "_place_until", now):
                _, pos = self._order_bottle()
                self._release_from = None if pos is None else (pos[0], pos[1], pos[2])
                self._release_t = now
                self._open_fingers()
                self._carry_attach = False
                self._place_stage = "ease"
                return
            if pinch is None:
                return
            dx, dy = desk[0] - pinch[0], desk[1] - pinch[1]
            bearing, forward = self._goal_bearing(dx, dy, yaw)
            front = self._lidar_sectors()["front"]
            if forward > 0.04 and front > 0.28 and abs(bearing) < 0.7:
                self.set_base_velocity(0.06, 0.35 * bearing)
            return
        self.set_base_velocity(0.0, 0.0)
        if self._ease_onto_desk():
            self.carried = []
            self.apply_pose(FOLDED_POSE, hold_s=1.0)
            self.job = "dwell_room"
            self._dwell_until = now + DWELL_SEC
            print("placed %s on the room-1204 desk" % ORDER_ITEM)

    def start_job(self):
        self.teleop = False
        self.carried = []
        self.pick_i = 0
        self.pick_name = ORDER_ITEM
        self._carry_attach = False
        self._gripper_node = None
        self._wrist_node_cached = None
        self._finger_links = None
        self.event = "job"
        node, pos = self._order_bottle()
        pinch = self._gripper_world()
        if (
            node is not None
            and pos is not None
            and not self._on_counter(pos)
            and pinch is not None
            and math.dist(pinch, (pos[0], pos[1], pos[2] + _BODY_CENTER_Z)) < 0.45
        ):
            self.set_hands(closed=True)
            self._carry_attach = True
            self.carried = [ORDER_ITEM]
            self.apply_pose(CARRY_POSE, hold_s=1.0)
            self.waypoints = [wp for wp in PATH_DELIVER if not (wp[0] > 7.5 and wp[1] < -4.2)]
            self.wp_index = 0
            self._reset_nav()
            self.job = "nav_deliver"
            self.event = "carrying"
            print("already holding %s, continuing to room-1204" % ORDER_ITEM)
            return
        self.apply_pose(FOLDED_POSE)
        self.set_hands(closed=False)
        if node is None or not self._on_counter(pos):
            print("counter bottle missing: %s is not on the kitchen worktop" % ORDER_ITEM)
        else:
            print(
                "counter bottle %s at (%.2f, %.2f, %.2f)"
                % (ORDER_ITEM, pos[0], pos[1], pos[2])
            )
        self._begin_approach()
        print("job start: grasp %s, then room-1204" % ORDER_ITEM)

    def _reset_nav(self):
        self._stuck_since = None
        self._stuck_pose = None
        self._recover_until = 0.0
        self._recover_turn = 0.0
        self._stuck_counts = {}
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
        if self._carry_attach:
            self._sync_carried_to_tool()
        if self.job is None or self.posing():
            self.set_base_velocity(0.0, 0.0)
            return
        if self.job == "approach":
            if self.robot.getTime() >= getattr(self, "_fold_again", 0.0):
                self.apply_pose(FOLDED_POSE)
                self.set_hands(closed=False)
                self._fold_again = self.robot.getTime() + 1.0
            if not self.follow_waypoints():
                return
            _, _, _, yaw = self.get_pose()
            err = (COUNTER_YAW - yaw + math.pi) % (2.0 * math.pi) - math.pi
            if abs(err) > 0.18:
                self.set_base_velocity(0.0, math.copysign(0.6, err if err != 0.0 else 1.0))
                return
            x, y, _, _ = self.get_pose()
            print("at bottle stance (%.2f, %.2f)" % (x, y))
            self.set_base_velocity(0.0, 0.0)
            self.job = "reach"
            self.event = "waiting_load"
            self.apply_pose(REACH_POSE, hold_s=2.6)
            self.set_hands(closed=False)
            self.publish()
            return
        if self.job == "reach":
            self.set_base_velocity(0.0, 0.0)
            node, pos = self._order_bottle()
            if node is None or not self._on_counter(pos):
                print("pickup held: %s is not on the kitchen counter" % ORDER_ITEM)
                self._carry_attach = False
                self.carried = []
                self.event = "waiting_load"
                self.job = None
                self.set_hands(closed=False)
                self.publish()
                return
            self.set_hands(closed=False)
            self.job = "grasp"
            self._grasp_until = self.robot.getTime() + 18.0
            self._jaws_closed_at = None
            self._jaw_align = None
            self._jaw_next = 0.0
            return
        if self.job == "grasp":
            now = self.robot.getTime()
            if getattr(self, "_jaws_closed_at", None) is not None:
                self.set_base_velocity(0.0, 0.0)
                self._sync_carried_to_tool()
                if now < self._jaws_closed_at + 0.55:
                    return
                node, pos = self._order_bottle()
                self.carried = [ORDER_ITEM]
                self.event = "pickup"
                self.publish()
                print(
                    "pickup t=%.1f items=%s bottle=(%.2f, %.2f, %.2f)"
                    % (self.robot.getTime(), self.carried, pos[0], pos[1], pos[2])
                )
                self.apply_pose(CARRY_POSE, hold_s=1.4)
                self.job = "fold_carry"
                return
            self.set_base_velocity(0.0, 0.0)
            node, pos = self._order_bottle()
            if node is None or not self._on_counter(pos):
                print("pickup held: %s left the counter before the fingers closed" % ORDER_ITEM)
                self._carry_attach = False
                self.carried = []
                self.event = "waiting_load"
                self.job = None
                self.set_hands(closed=False)
                self.publish()
                return
            self.pick_name = ORDER_ITEM
            pinch = self._gripper_world()
            body = (pos[0], pos[1], pos[2] + _BODY_CENTER_Z)
            gap = None
            if pinch is not None:
                gap = math.sqrt(sum((body[i] - pinch[i]) ** 2 for i in range(3)))
            if gap is not None and gap <= 0.055:
                self.set_hands(closed=True)
                self._carry_attach = True
                self._jaws_closed_at = now
                self._sync_carried_to_tool()
                print("jaws on bottle, gap %.3f m" % gap)
                return
            if now >= getattr(self, "_grasp_until", 0.0):
                self._carry_attach = False
                self.carried = []
                self.event = "waiting_load"
                self.job = None
                self.set_hands(closed=False)
                print("pickup held: gripper did not take the counter bottle")
                self.publish()
                return
            if pinch is not None:
                if gap is None or gap > 0.12:
                    if now >= getattr(self, "_reach_again", 0.0):
                        self.apply_pose(REACH_POSE)
                        self._reach_again = now + 0.8
                dx, dy = body[0] - pinch[0], body[1] - pinch[1]
                _, _, _, yaw = self.get_pose()
                bearing, forward = self._goal_bearing(dx, dy, yaw)
                yaw_err = (COUNTER_YAW - yaw + math.pi) % (2.0 * math.pi) - math.pi
                if abs(yaw_err) > 0.12:
                    self.set_base_velocity(0.0, math.copysign(0.35, yaw_err if yaw_err else 1.0))
                elif math.hypot(dx, dy) > 0.025:
                    self.set_base_velocity(max(-0.04, min(0.05, forward)), 0.3 * bearing)
            return
        if self.job == "fold_carry":
            self.set_base_velocity(0.0, 0.0)
            self.waypoints = list(PATH_DELIVER)
            self.wp_index = 0
            self._reset_nav()
            self.job = "nav_deliver"
            self.event = "carrying"
            return
        if self.job == "nav_deliver":
            if self.follow_waypoints():
                self.job = "place"
                self._place_stage = "aim"
                self.event = "at_dropoff"
                self.publish()
                self.set_base_velocity(0.0, 0.0)
            return
        if self.job == "place":
            self._tick_place()
            return
        if self.job == "dwell_room":
            self.set_base_velocity(0.0, 0.0)
            if self.robot.getTime() >= self._dwell_until:
                self.event = "delivery"
                self.publish()
                print("delivery t=%.1f room-1204" % self.robot.getTime())
                self.waypoints = list(PATH_DOCK)
                self.wp_index = 0
                self._reset_nav()
                self.job = "nav_dock"
                self.event = "returning"
            return
        if self.job == "nav_dock":
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
            "job": self.job or "",
        }
        grip = self._gripper_world()
        if grip is not None:
            payload["gripper"] = [round(grip[0], 3), round(grip[1], 3), round(grip[2], 3)]
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
            if steps % 8 == 0:
                self._paint_sensors()
            if steps % 16 == 0:
                self.publish()


def main():
    ButlerServeController().run()


if __name__ == "__main__":
    main()
