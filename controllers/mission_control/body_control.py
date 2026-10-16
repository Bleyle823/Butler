from controller import Robot, Supervisor
import numpy as np
from collections import defaultdict
import math

from py_trees.behaviour import Behaviour
from py_trees.common import Status
from py_trees.composites import Sequence

# Counter item poses in kitchen.wbt (world XY); used to ignore decorative drinks.
KITCHEN_ITEM_XY = {
    "heineken beer": np.array([1.714, 0.704]),
    "beverage can": np.array([1.71, -0.302]),
    "water bottle": np.array([1.93, 0.494]),
}
KITCHEN_ITEM_RADIUS = 0.28


def recognition_model(model, object_names):
    if model in object_names:
        return model
    if model == "beer bottle" and "heineken beer" in object_names:
        return "heineken beer"
    if model == "can" and "beverage can" in object_names:
        return "beverage can"
    return None


def near_kitchen_item(item_name, world_position):
    anchor = KITCHEN_ITEM_XY.get(item_name)
    if anchor is None:
        return True
    return np.linalg.norm(world_position[:2] - anchor) <= KITCHEN_ITEM_RADIUS


class change_height_to(Behaviour):
    def __init__(self,name,blackboard,object_name=None,zone=None):
    
        super(change_height_to, self).__init__(name)
        self.robot = blackboard.read("robot")
        self.timestep = int(self.robot.getBasicTimeStep())
        self.blackboard = blackboard
        
        self.zone = zone
        self.object_name = object_name
        
        self.joint_name = "torso_lift_joint"
        
        self.motor = self.blackboard.read("motors_dict")[self.joint_name]
        self.motor_sensor = self.blackboard.read("encoders_dict")[self.joint_name]
        
    def setup(self):
        self.motor_sensor.enable(self.timestep)
        self.camera_translation = self.blackboard.read("GPSTC")  # [x, y, z], known distance from gps to camera

    def initialise(self):
        self._missing_location = False
        if self.object_name:
            locations = self.blackboard.read("object_location")
            if self.object_name not in locations or not locations[self.object_name]:
                self._missing_location = True
                self.feedback_message = f"missing location for {self.object_name}"
                return
            locations_list = locations[self.object_name]
            self.location = locations_list[0]
            print(f"location of {self.object_name}: ", self.location)
        else:
            self.location = self.blackboard.read('drop_zones')[self.zone]
            
        self.target = min(self.location[2] - 0.63, 0.35)
        self.motor.setPosition(self.target)

    def update(self):
        if self._missing_location:
            return Status.FAILURE

        current = self.motor_sensor.getValue()
        error = abs(self.target - current)
        
        if error < 0.01:
            return Status.SUCCESS
        else:
            self.motor.setPosition(self.target)
            return Status.RUNNING
        
    def terminate(self, new_status):
        if new_status == Status.SUCCESS:
            print(f"height adjusted")
            
class search(Behaviour): #returns positions of specified objects in world coordinates
    def __init__(self,name,blackboard,object_names):
    
        super(search, self).__init__(name)
        self.robot = blackboard.read("robot")
        self.timestep = int(self.robot.getBasicTimeStep())
        self.blackboard = blackboard
        self.object_names = object_names
        
    def setup(self):
        self.camera = self.robot.getDevice("camera")
        
        self.gps = self.robot.getDevice('gps')
        self.compass = self.robot.getDevice('compass')
        self.gps.enable(self.timestep)
        self.compass.enable(self.timestep)

    def initialise(self):
        self.camera.enable(self.timestep)
        self.camera.recognitionEnable(self.timestep)
        self.camera_translation = self.blackboard.read("GPSTC")
        self.object_dict = {} #location storage

    def update(self):
        #print(self.object_name)
        objects = self.camera.getRecognitionObjects()

        # Get camera position in world coordinates
        wX = self.worldX = self.gps.getValues()[0] #position of robot
        wY = self.worldY = self.gps.getValues()[1] #position of robot
        #print("gps", wX, wY)
        theta=np.arctan2(self.compass.getValues()[0],self.compass.getValues()[1])
        
        if theta > np.pi: #fix calc issue when > 180 degrees
            theta = theta - 2*np.pi
        angle1 = theta #math.degrees(theta)
        #print(angle1)
        
        #rotation matrix
        R = np.array([
            [np.cos(angle1), -np.sin(angle1)],
            [np.sin(angle1),  np.cos(angle1)]
        ])
        
        camera_rotation = R.dot(self.camera_translation[:2])
        camera_position = np.array([camera_rotation[0]+wX,camera_rotation[1]+wY,self.camera_translation[2]])

        for obj in objects:
            item_name = recognition_model(obj.getModel(), self.object_names)
            if not item_name:
                continue
            relative_position = obj.getPosition()
            xy_rotated = R.dot(relative_position[:2])
            relative_position = np.array([xy_rotated[0], xy_rotated[1], relative_position[2]])
            world_position = np.array(np.round(camera_position + relative_position, 3))
            if not near_kitchen_item(item_name, world_position):
                continue
            if item_name not in self.object_dict:
                self.object_dict[item_name] = []
            self.object_dict[item_name].append(world_position)

        for item_name in self.object_names:
            positions = self.object_dict.get(item_name)
            if not positions:
                continue
            anchor = KITCHEN_ITEM_XY.get(item_name)
            if anchor is not None and len(positions) > 1:
                best = min(positions, key=lambda p: np.linalg.norm(p[:2] - anchor))
                self.object_dict[item_name] = [best]

        if all(name in self.object_dict and self.object_dict[name] for name in self.object_names):
            self.blackboard.write("object_location", self.object_dict)
            print(self.object_dict)
            self.camera.recognitionDisable()
            return Status.SUCCESS
        elif len(self.object_dict) > 0:
            self.feedback_message = f"found {list(self.object_dict.keys())}, waiting for {self.object_names}"
            return Status.RUNNING
        else:
            return Status.RUNNING
        
    def terminate(self, new_status):
        if new_status == Status.SUCCESS:
            #self.camera.disable()
            print(f"Found the objects listed")