"""World commander stub.

KeeperHub will later talk only to this process. Webots still never talks
to peaq or Circle. Keys 1-5 toggle hotel doors while this robot is selected.
"""

from controller import Supervisor

DOOR_DEFS = (
    "LOBBY_DOOR",
    "RESTAURANT_DOOR",
    "ROOM_1204_DOOR",
    "ROOM_1205_DOOR",
    "ROOM_1206_DOOR",
)
CLOSED = [0, 0, 1, 0]
OPEN = [0, 0, 1, 1.45]


class ButlerSupervisor:
    def __init__(self):
        self.robot = Supervisor()
        self.timestep = int(self.robot.getBasicTimeStep())
        self.keyboard = self.robot.getKeyboard()
        self.keyboard.enable(self.timestep)
        self._door_open = {name: True for name in DOOR_DEFS}
        print("butler_supervisor: keys 1-5 toggle doors. Robot still holds no chain keys.")

    def set_door(self, def_name, open_door):
        node = self.robot.getFromDef(def_name)
        if node is None:
            return
        field = node.getField("leafRotation")
        if field is None:
            return
        field.setSFRotation(OPEN if open_door else CLOSED)
        self._door_open[def_name] = open_door

    def toggle_door(self, def_name):
        self.set_door(def_name, not self._door_open.get(def_name, False))

    def run(self):
        while self.robot.step(self.timestep) != -1:
            key = self.keyboard.getKey()
            while key != -1:
                if key == ord("1"):
                    self.toggle_door("LOBBY_DOOR")
                elif key == ord("2"):
                    self.toggle_door("RESTAURANT_DOOR")
                elif key == ord("3"):
                    self.toggle_door("ROOM_1204_DOOR")
                elif key == ord("4"):
                    self.toggle_door("ROOM_1205_DOOR")
                elif key == ord("5"):
                    self.toggle_door("ROOM_1206_DOOR")
                key = self.keyboard.getKey()


if __name__ == "__main__":
    ButlerSupervisor().run()
