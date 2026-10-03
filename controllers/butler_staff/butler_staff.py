"""Kitchen staff: stand at the load point and reach the pizza and drink onto the tray."""

from __future__ import annotations

import json
import math

from controller import Supervisor

ROOT_HEIGHT = 1.27
STAFF_DEF = "KITCHEN_STAFF"
ROBOT_DEF = "SERVEBOT_1"
# West of the chest tray. Robot stops south of the stand, facing north.
STAFF_XY = (8.50, -2.82)
STAFF_YAW = 0.0
COUNTER_STANCE = (8.98, -3.18)
# Same robot-frame wells butler_serve uses. Pizza z is box centre on the deck.
TRAY = {
    "PIZZA_BOX": (0.36, 0.02, 0.81),
    "DRINK_BOTTLE": (0.30, -0.10, 0.79),
}

JOINT_NAMES = (
    "leftArmAngle",
    "leftLowerArmAngle",
    "leftHandAngle",
    "rightArmAngle",
    "rightLowerArmAngle",
    "rightHandAngle",
    "leftLegAngle",
    "leftLowerLegAngle",
    "leftFootAngle",
    "rightLegAngle",
    "rightLowerLegAngle",
    "rightFootAngle",
    "headAngle",
)
HOLD_ARMS = (-1.20, -0.45, 0.1, -1.20, -0.45, 0.1)
REACH_ARMS = (-1.55, -0.20, 0.0, -1.55, -0.20, 0.0)
REST_ARMS = (0.12, -0.20, 0.0, 0.12, -0.20, 0.0)
IDLE_LEGS = (0.0, 0.12, 0.0, 0.0, 0.12, 0.0, 0.08)


def _yaw_of(node):
    rot = node.getOrientation()
    return math.atan2(rot[3], rot[0])


class KitchenStaff:
    def __init__(self):
        self.robot = Supervisor()
        self.timestep = int(self.robot.getBasicTimeStep())
        self.staff = self.robot.getFromDef(STAFF_DEF)
        if self.staff is None:
            print("kitchen staff: missing DEF %s" % STAFF_DEF)
            return
        self.translation = self.staff.getField("translation")
        self.rotation = self.staff.getField("rotation")
        self.joints = [self.staff.getField(name) for name in JOINT_NAMES]
        self.stage = "wait_robot"
        self.hold_until = 0.0
        self.holding = ["PIZZA_BOX", "DRINK_BOTTLE"]
        self._lock_item("PIZZA_BOX", True)
        self._lock_item("DRINK_BOTTLE", True)
        self._stand()
        self._set_arms(HOLD_ARMS)
        self._sync_held()
        print("kitchen staff waiting with pizza and drink")

    def _now(self):
        return self.robot.getTime()

    def _stand(self):
        self.translation.setSFVec3f([STAFF_XY[0], STAFF_XY[1], ROOT_HEIGHT])
        self.rotation.setSFRotation([0, 0, 1, STAFF_YAW])
        for index, value in enumerate(IDLE_LEGS):
            field = self.joints[6 + index] if 6 + index < len(self.joints) else None
            if field is not None:
                field.setSFFloat(value)

    def _set_arms(self, arms):
        for index, value in enumerate(arms):
            field = self.joints[index]
            if field is not None:
                field.setSFFloat(value)

    def _lock_item(self, name, locked):
        node = self.robot.getFromDef(name)
        if node is None:
            return
        field = node.getField("locked")
        if field is not None:
            field.setSFBool(locked)

    def _move_item(self, name, point):
        node = self.robot.getFromDef(name)
        if node is None:
            return
        node.getField("translation").setSFVec3f([point[0], point[1], point[2]])
        node.getField("rotation").setSFRotation([0, 0, 1, 0])
        node.resetPhysics()

    def _hand_world(self, side):
        pos = self.staff.getPosition()
        yaw = _yaw_of(self.staff)
        c, s = math.cos(yaw), math.sin(yaw)
        along = 0.28 if self.stage == "reach" else 0.20
        side_off = 0.16 if side == "left" else -0.16
        z = 1.02 if self.stage == "reach" else 1.08
        return (pos[0] + along * c - side_off * s, pos[1] + along * s + side_off * c, z)

    def _sync_held(self):
        if "PIZZA_BOX" in self.holding:
            hx, hy, hz = self._hand_world("left")
            self._move_item("PIZZA_BOX", (hx, hy, hz - 0.03))
        if "DRINK_BOTTLE" in self.holding:
            hx, hy, hz = self._hand_world("right")
            self._move_item("DRINK_BOTTLE", (hx, hy, hz - 0.08))

    def _robot_pose(self):
        node = self.robot.getFromDef(ROBOT_DEF)
        if node is None:
            return None
        pos = node.getPosition()
        if pos is None or any(math.isnan(v) for v in pos[:2]):
            return None
        return pos[0], pos[1], pos[2], _yaw_of(node)

    def _on_tray(self, name):
        pose = self._robot_pose()
        if pose is None:
            return None
        rx, ry, rz, yaw = pose
        forward, left, up = TRAY[name]
        c, s = math.cos(yaw), math.sin(yaw)
        return (rx + forward * c - left * s, ry + forward * s + left * c, rz + up)

    def _robot_waiting(self):
        node = self.robot.getFromDef(ROBOT_DEF)
        if node is None:
            return False
        raw = node.getField("customData")
        if raw is None:
            return False
        try:
            data = json.loads(raw.getSFString() or "{}")
        except (TypeError, ValueError):
            return False
        if data.get("event") != "waiting_load":
            return False
        pose = data.get("pose")
        if not pose or len(pose) < 2:
            return False
        return math.hypot(pose[0] - COUNTER_STANCE[0], pose[1] - COUNTER_STANCE[1]) < 0.80

    def _seat(self, name):
        well = self._on_tray(name)
        if well is None:
            return
        self._move_item(name, well)
        self._lock_item(name, True)
        if name in self.holding:
            self.holding.remove(name)

    def tick(self):
        if self.staff is None:
            return
        self._stand()
        now = self._now()
        if now < self.hold_until:
            self._sync_held()
            return
        if self.stage == "wait_robot":
            self._set_arms(HOLD_ARMS)
            self._sync_held()
            if self._robot_waiting():
                print("staff: stretching to the tray")
                self.stage = "reach"
                self._set_arms(REACH_ARMS)
                self.hold_until = now + 0.9
            return
        if self.stage == "reach":
            self._set_arms(REACH_ARMS)
            self._sync_held()
            self._seat("PIZZA_BOX")
            self._seat("DRINK_BOTTLE")
            self._set_arms(REST_ARMS)
            self.stage = "done"
            print("staff: pizza and drink on the tray")
            return
        if self.stage == "done":
            self._set_arms(REST_ARMS)
            if self._robot_waiting() and not self.holding:
                pizza = self.robot.getFromDef("PIZZA_BOX")
                pose = self._robot_pose()
                if pizza is not None and pose is not None:
                    pos = pizza.getPosition()
                    if math.hypot(pos[0] - pose[0], pos[1] - pose[1]) > 1.5:
                        self.holding = ["PIZZA_BOX", "DRINK_BOTTLE"]
                        self.stage = "wait_robot"

    def run(self):
        while self.robot.step(self.timestep) != -1:
            self.tick()


if __name__ == "__main__":
    KitchenStaff().run()
