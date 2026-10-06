"""Read the kitchen scene and post servebot-1 telemetry.

This controller never sets a motor position and never moves a node.
mission_control still picks up the jars and places them on the table.
"""

import json
import math
import threading
import urllib.request
from controller import Supervisor

ROBOT_NAME = "servebot-1"
JARS = ("honey jar", "jam jar 1", "jam jar 2")
DROP_ZONES = ((-0.38, -0.68), (-0.55, -1.39), (-0.54, -2.17))
DROP_RADIUS = 0.28
CARRY_RADIUS = 0.55
MOVE_EPS = 0.12
BRIDGE = "http://127.0.0.1:8787/telemetry"


_post_lock = threading.Lock()
_post_busy = False


def post(body):
    global _post_busy
    with _post_lock:
        if _post_busy:
            return
        _post_busy = True

    def send():
        global _post_busy
        data = json.dumps(body).encode("utf-8")
        request = urllib.request.Request(
            BRIDGE,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=0.05) as response:
                response.read()
        except Exception:
            pass
        finally:
            with _post_lock:
                _post_busy = False

    threading.Thread(target=send, daemon=True).start()


def node_name(node):
    field = node.getField("name")
    if field is None:
        return ""
    return field.getSFString()


def find_named(root_children, name):
    for index in range(root_children.getCount()):
        node = root_children.getMFNode(index)
        if node is None:
            continue
        if node_name(node) == name:
            return node
    return None


def xy(position):
    return position[0], position[1]


def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def yaw_of(node):
    matrix = node.getOrientation()
    return math.atan2(matrix[3], matrix[0])


robot = Supervisor()
timestep = int(robot.getBasicTimeStep())
root_children = robot.getRoot().getField("children")
serve = None
jars = {}
starts = {}
step_count = 0

while robot.step(timestep) != -1:
    step_count += 1
    if serve is None:
        serve = find_named(root_children, ROBOT_NAME)
    if len(jars) < len(JARS):
        for jar_name in JARS:
            if jar_name not in jars:
                node = find_named(root_children, jar_name)
                if node is not None:
                    jars[jar_name] = node
                    starts[jar_name] = xy(node.getPosition())
    if serve is None:
        continue

    pose = serve.getPosition()
    robot_xy = xy(pose)
    carried = []
    delivered = []
    for jar_name, node in jars.items():
        position = node.getPosition()
        jar_xy = xy(position)
        moved = distance(jar_xy, starts[jar_name]) > MOVE_EPS
        on_table = any(distance(jar_xy, zone) <= DROP_RADIUS for zone in DROP_ZONES)
        with_robot = distance(jar_xy, robot_xy) <= CARRY_RADIUS
        if moved and on_table:
            delivered.append(jar_name)
        elif moved and with_robot:
            carried.append(jar_name)

    if delivered:
        event = "delivery"
    elif carried:
        event = "pickup"
    else:
        event = ""

    if step_count % 8 != 0:
        continue

    post({
        "name": ROBOT_NAME,
        "pose": [pose[0], pose[1], pose[2], yaw_of(serve)],
        "battery": 1.0,
        "event": event,
        "carried": carried or delivered,
    })
