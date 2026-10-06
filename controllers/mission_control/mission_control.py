"""main controller."""

import py_trees
import numpy as np

from controller import Robot, Supervisor

from py_trees.composites import Sequence, Parallel, Selector
from py_trees.behaviour import Behaviour
from py_trees.common import Status

from arm_control import open_gripper, grab_item, arm_travel_position, arm_extend_position, lift_arm
from body_control import change_height_to, search
from travel_control import route, move, get_in_position, back_up, rotate_to_face
from mapping import test_for_map, map_environment


robot = Supervisor()
timestep = int(robot.getBasicTimeStep())

#---------------------------------------------------

motors = {
    "arm_1_joint": robot.getDevice("arm_1_joint"),
    "arm_2_joint": robot.getDevice("arm_2_joint"),
    "arm_3_joint": robot.getDevice("arm_3_joint"),
    "arm_4_joint": robot.getDevice("arm_4_joint"),
    "arm_5_joint": robot.getDevice("arm_5_joint"),
    "arm_6_joint": robot.getDevice("arm_6_joint"),
    "arm_7_joint": robot.getDevice("arm_7_joint"),
    "torso_lift_joint": robot.getDevice("torso_lift_joint")
    # Add more as needed
}

JC = { 'openGripper' : {'gripper_left_finger_joint' : 0.045,
                        'gripper_right_finger_joint': 0.045},
       'closeGripper': {'gripper_left_finger_joint' : 0.0,
                        'gripper_right_finger_joint': 0.0}}
encoders = {
    "arm_1_joint": robot.getDevice("arm_1_joint_sensor"),
    "arm_2_joint": robot.getDevice("arm_2_joint_sensor"),
    "arm_3_joint": robot.getDevice("arm_3_joint_sensor"),
    "arm_4_joint": robot.getDevice("arm_4_joint_sensor"),
    "arm_5_joint": robot.getDevice("arm_5_joint_sensor"),
    "arm_6_joint": robot.getDevice("arm_6_joint_sensor"),
    "arm_7_joint": robot.getDevice("arm_7_joint_sensor"),
    "torso_lift_joint": robot.getDevice("torso_lift_joint_sensor"),
    "gripper_left_finger_joint": robot.getDevice("gripper_left_sensor_finger_joint"),
    "gripper_right_finger_joint": robot.getDevice("gripper_right_sensor_finger_joint")
}
#for encoder in encoders.values():    encoder.enable(timestep)

#---------------------------target for motors in arm----------
targets = {
    "arm_1_joint": 1.6,
    "arm_2_joint": 1,
    "arm_3_joint": 2,
    "arm_4_joint": 2,
    "arm_5_joint": 0,
    "arm_6_joint": 0,
    "arm_7_joint": 1.6,
    "torso_lift_joint": 0.28,
}

map_WP = [(0.3,0),(0.42,-.31),(0.45,-2.5),(-0.66,-3.2),(-1.5,-2.9),(-1.71,-1),(-1.36,0),(-0.3,0.4)]
camera_to_gripper = np.array([0.5,0,-0.25]) #distances
gps_to_camera = np.array([0.23,0,0.9457]) #distances
drop_zones = np.array([[-0.38,-0.68,0.75],[-0.55,-1.39,0.75],[-0.54,-2.17,0.75]])
drop_positions = [(189,100),(200,160),(195,229)]
grab_position = (170,75)
#---------------------Blackboard for data storage in BT-------

class BB:
    def __init__(self):
        self.data = {}
    def write(self,key,value):
        self.data[key] = value
    def read(self,key):
        return self.data.get(key)

blackboard = BB()
blackboard.write('robot',robot)
blackboard.write('motors_dict',motors)
blackboard.write('encoders_dict',encoders)
blackboard.write('targets_dict',targets)
blackboard.write('WP',map_WP)
blackboard.write('Grip',JC)
blackboard.write('GPSTC',gps_to_camera)
blackboard.write('CTG',camera_to_gripper)
blackboard.write('drop_zones',drop_zones)
blackboard.write('drop_positions',drop_positions)

class update(Behaviour):
    def __init__(self, name, blackboard, key1, key2, change):
        super(update, self).__init__(name)
        self.blackboard = blackboard
        self.key1 = key1
        self.key2 = key2
        self.change = change

    def initialise(self):
        pass

    def update(self):
        modify = self.blackboard.read(self.key1)
        if modify is not None:
            modify[self.key2] = self.change
            self.blackboard.write(self.key1, modify)
            return Status.SUCCESS
        else:
            print(f"Key '{self.key1}' not found in blackboard.")
            return Status.FAILURE

#--------------------------------------------------

#The Behaviour Tree (BT)------------------------------------------------------

BT = Sequence("main", children=[
        
        #map out the floor if it DNE
        arm_travel_position("get ready to move",blackboard),
        Selector("Does Map Exist?", children=[
            test_for_map("Test for map"),
            Parallel("Mapping",policy=py_trees.common.ParallelPolicy.SuccessOnOne(), children =[
                map_environment("Map the environment",blackboard),
                move("Move around the table",blackboard)
                ])],memory=True),
                
            #find and pick up the first jar (honey)
            route("compute path to counter",blackboard,grab_position),
            move("move to counter",blackboard),
            search("look for honey", blackboard, ["honey jar","jam jar"]),
            change_height_to("adjust height",blackboard,object_name="honey jar"),
            rotate_to_face("honey jar",blackboard,object_name="honey jar"),
            arm_extend_position("arm grab ready", blackboard),
            open_gripper("open grip", blackboard),
            get_in_position("approach honey",blackboard,object_name="honey jar"),
            grab_item("grab honey jar",blackboard),
            lift_arm("pick up honey jar",blackboard),
            back_up("pull back", blackboard),
            back_up("pull back", blackboard),
            
            #place the honey on the table
            route("compute path to spot 1",blackboard,drop_positions[0]),
            move("move to spot 1",blackboard),
            rotate_to_face("spot 1",blackboard,zone=0),
            get_in_position("approach spot 1",blackboard,zone=0),
            arm_extend_position("arm place ready", blackboard),
            change_height_to("adjust height",blackboard,zone=0),
            open_gripper("release item", blackboard),
            back_up("pull back", blackboard),
            lift_arm("move out of way",blackboard),
            
            #go back and grab jar 2, then put it on the table at spot 2
            route("compute path to counter",blackboard,grab_position),
            move("move to counter",blackboard),
            
            #search("look for jam", blackboard, "jam jar"),
            change_height_to("adjust height",blackboard,object_name="jam jar"),
            arm_travel_position("get ready to move",blackboard),
            rotate_to_face("jam 1",blackboard,object_name="jam jar"),
            arm_extend_position("arm place ready", blackboard),
            get_in_position("approach jam 1",blackboard,object_name="jam jar"),
            grab_item("grab jam",blackboard),
            lift_arm("pick up jam",blackboard),
            back_up("pull back", blackboard),
            back_up("pull back", blackboard),
            
            route("compute path to table staging area",blackboard,drop_positions[1]),
            move("move to spot",blackboard),
            rotate_to_face("spot 2",blackboard,zone=1),
            arm_extend_position("arm place ready", blackboard),
            get_in_position("approach spot 2",blackboard,zone=1),
            change_height_to("adjust height",blackboard,zone=1),
            open_gripper("release item", blackboard),
            back_up("pull back", blackboard),
            lift_arm("move out of way",blackboard),
            
            #go back and grab jar 3, then put it on the table at spot 3
            route("compute path to counter",blackboard,grab_position),
            move("move to counter",blackboard),
            
            change_height_to("adjust height",blackboard,object_name="jam jar"),
            arm_travel_position("get ready to move",blackboard),
            rotate_to_face("jam 2",blackboard,object_name="jam jar"),
            arm_extend_position("arm place ready", blackboard),
            get_in_position("approach jam 2",blackboard,object_name="jam jar"),
            grab_item("grab jam",blackboard),
            lift_arm("pick up jam",blackboard),
            back_up("pull back", blackboard),
            back_up("pull back", blackboard),
            
            route("compute path to table staging area",blackboard,drop_positions[2]),
            move("move to spot",blackboard),
            rotate_to_face("spot 3",blackboard,zone=2),
            get_in_position("approach spot 3",blackboard,zone=2),
            arm_extend_position("arm place ready", blackboard),
            change_height_to("adjust height",blackboard,zone=2),
            open_gripper("release item", blackboard),
            back_up("pull back", blackboard),
            lift_arm("move out of way",blackboard),
            
            route("compute path to counter",blackboard,grab_position),
            #arm_travel_position("get ready to move",blackboard),
            move("move to counter",blackboard),

        ],memory=True)

BT.setup_with_descendants()
#-----------------------------------------------------------------------------

#RUN BT
while robot.step(timestep) != 1:
    BT.tick_once()
    if BT.status != py_trees.common.Status.RUNNING:
        print("DONE")
        break