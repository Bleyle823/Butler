from controller import Robot, Supervisor
import numpy as np
from collections import defaultdict
import math

from py_trees.behaviour import Behaviour
from py_trees.common import Status
from py_trees.composites import Sequence

class move_arm_manual(Behaviour):
    def __init__(self,name,blackboard,number):
    
        super(move_arm_manual, self).__init__(name)
        self.robot = blackboard.read("robot")
        self.timestep = int(self.robot.getBasicTimeStep())
        self.blackboard = blackboard
        
        self.joint_name = f"arm_{number}_joint"
        self.target = blackboard.read("targets_dict")[self.joint_name]
        self.arm_motor = self.blackboard.read("motors_dict")[self.joint_name]
        self.motor_sensor = self.blackboard.read("encoders_dict")[self.joint_name]
        
    def setup(self):
        self.motor_sensor.enable(self.timestep)

    def initialise(self):
        self.target = self.blackboard.read("targets_dict")[self.joint_name]
        self.arm_motor.setPosition(self.target)

    def update(self):
        
        current = self.motor_sensor.getValue()
        error = abs(self.target - current)
        
        if error < 0.01:
            return Status.SUCCESS
        else:
            self.arm_motor.setPosition(self.target)
            return Status.RUNNING
        
    def terminate(self, new_status):
        if new_status == Status.SUCCESS:
            pass
            #print(f"{self.joint_name} reached specified position")
            
class arm_travel_position(Behaviour):
    def __init__(self,name,blackboard):
        
        super(arm_travel_position, self).__init__(name)
        self.robot = blackboard.read("robot")
        self.timestep = int(self.robot.getBasicTimeStep())
        self.blackboard = blackboard
        
        self.speed = 1.5
        self.order = [4,1,2]
        self.targets = {4:2,1:1.6,2:0}
        
    def setup(self):
        for number in self.order:
            encoder = self.robot.getDevice(f"arm_{number}_joint_sensor")
            encoder.enable(self.timestep)

    def initialise(self):
        for number in self.order:
            joint_name = f"arm_{number}_joint"
            target = self.targets[number]
            arm_motor = self.robot.getDevice(joint_name)
            arm_motor.setVelocity(self.speed)
            arm_motor.setPosition(target)

    def update(self):
    
        for number in self.order:
            joint_name = f"arm_{number}_joint"
            target = self.targets[number]
            arm_motor = self.robot.getDevice(joint_name)
            arm_motor.setPosition(target)
        
        i = 0
        for number in self.order:
            target = self.targets[number]
            sensor = self.robot.getDevice(f"arm_{number}_joint_sensor")
            current = sensor.getValue()
            error = abs(target - current)
            if error < 0.01:
                i += 1

        if i == len(self.order):
            return Status.SUCCESS
        else:
            return Status.RUNNING
        
    def terminate(self, new_status):
        if new_status == Status.SUCCESS:
            print("position achieved")
            
class arm_extend_position(Behaviour):
    def __init__(self,name,blackboard):
        
        super(arm_extend_position, self).__init__(name)
        self.robot = blackboard.read("robot")
        self.timestep = int(self.robot.getBasicTimeStep())
        self.blackboard = blackboard
        
        self.speed = 1.5
        self.order = [1,2,3,4,7]
        self.targets = {1:1.6,2:0,3:0,4:0,7:1.6}
        
    def setup(self):
        for number in self.order:
            encoder = self.robot.getDevice(f"arm_{number}_joint_sensor")
            encoder.enable(self.timestep)

    def initialise(self):
        for number in self.order:
            joint_name = f"arm_{number}_joint"
            target = self.targets[number]
            arm_motor = self.robot.getDevice(joint_name)
            arm_motor.setVelocity(self.speed)
            arm_motor.setPosition(target)

    def update(self):
    
        for number in self.order:
            joint_name = f"arm_{number}_joint"
            target = self.targets[number]
            arm_motor = self.robot.getDevice(joint_name)
            arm_motor.setPosition(target)
        
        i = 0
        for number in self.order:
            target = self.targets[number]
            sensor = self.robot.getDevice(f"arm_{number}_joint_sensor")
            current = sensor.getValue()
            error = abs(target - current)
            if error < 0.01:
                i += 1

        if i == len(self.order):
            return Status.SUCCESS
        else:
            return Status.RUNNING
        
    def terminate(self, new_status):
        if new_status == Status.SUCCESS:
            print("position achieved")
            
class lift_arm(Behaviour):
    def __init__(self,name,blackboard):
        
        super(lift_arm, self).__init__(name)
        self.robot = blackboard.read("robot")
        self.timestep = int(self.robot.getBasicTimeStep())
        self.blackboard = blackboard
        
        self.speed = 1
        self.order = [1,2,4,7]
        self.targets = {1:1.6,2:1,4:1,7:1.6}
        
    def setup(self):
        for number in self.order:
            encoder = self.robot.getDevice(f"arm_{number}_joint_sensor")
            encoder.enable(self.timestep)

    def initialise(self):
        for number in self.order:
            joint_name = f"arm_{number}_joint"
            target = self.targets[number]
            arm_motor = self.robot.getDevice(joint_name)
            arm_motor.setVelocity(self.speed)
            arm_motor.setPosition(target)

    def update(self):
    
        for number in self.order:
            joint_name = f"arm_{number}_joint"
            target = self.targets[number]
            arm_motor = self.robot.getDevice(joint_name)
            arm_motor.setPosition(target)
        
        i = 0
        for number in self.order:
            target = self.targets[number]
            sensor = self.robot.getDevice(f"arm_{number}_joint_sensor")
            current = sensor.getValue()
            error = abs(target - current)
            if error < 0.01:
                i += 1

        if i == len(self.order):
            return Status.SUCCESS
        else:
            return Status.RUNNING
        
    def terminate(self, new_status):
        if new_status == Status.SUCCESS:
            print("arm lifted")
            
class grab_item(Behaviour):
    def __init__(self,name,blackboard):
    
        super(grab_item, self).__init__(name)
        self.robot = blackboard.read("robot")
        self.timestep = int(self.robot.getBasicTimeStep())
        self.blackboard = blackboard
        
        self.grab = [blackboard.read('Grip')['openGripper'],blackboard.read('Grip')['closeGripper']]
        
        self.gripper_left_name = 'gripper_left_finger_joint'
        self.gripper_right_name = 'gripper_right_finger_joint'
        self.gripper_left = self.robot.getDevice(self.gripper_left_name)
        self.gripper_right = self.robot.getDevice(self.gripper_right_name)
        self.sensor_left = self.blackboard.read("encoders_dict")[self.gripper_left_name]
        self.sensor_right = self.blackboard.read("encoders_dict")[self.gripper_right_name]
        
        self.open = self.grab[0][self.gripper_left_name]
        self.close = self.grab[1][self.gripper_left_name]
        
    def setup(self):
        #enable feedback
        self.gripper_left.enableForceFeedback(self.timestep)
        self.gripper_right.enableForceFeedback(self.timestep)
        
        self.sensor_left.enable(self.timestep)
        self.sensor_right.enable(self.timestep)

    def initialise(self):
        self.gripper_left.setPosition(self.close)
        self.gripper_right.setPosition(self.close)

    def update(self):
        
        feedback_left = self.gripper_left.getForceFeedback()
        feedback_right = self.gripper_left.getForceFeedback()
        
        total_feedback = feedback_left + feedback_right
        
        currentL = self.sensor_left.getValue()
        currentR = self.sensor_right.getValue()
        currentT = currentL + currentR
        
        if total_feedback >= -10:
            return Status.SUCCESS
        elif currentT < 0.01:
            print("did not grab anything!")
            return Status.FAILURE
        else:
            self.gripper_left.setPosition(self.close)
            self.gripper_right.setPosition(self.close)
            return Status.RUNNING
        
    def terminate(self, new_status):
        if new_status == Status.SUCCESS:
            print(f"object grabbed")
            
class open_gripper(Behaviour):
    def __init__(self,name,blackboard):
    
        super(open_gripper, self).__init__(name)
        self.robot = blackboard.read("robot")
        self.timestep = int(self.robot.getBasicTimeStep())
        self.blackboard = blackboard
        
        self.grab = [blackboard.read('Grip')['openGripper'],blackboard.read('Grip')['closeGripper']]
        
        self.gripper_left_name = 'gripper_left_finger_joint'
        self.gripper_right_name = 'gripper_right_finger_joint'
        self.gripper_left = self.robot.getDevice(self.gripper_left_name)
        self.gripper_right = self.robot.getDevice(self.gripper_right_name)
        self.sensor_left = self.blackboard.read("encoders_dict")[self.gripper_left_name]
        self.sensor_right = self.blackboard.read("encoders_dict")[self.gripper_right_name]
        
        self.open = self.grab[0][self.gripper_left_name]
        self.close = self.grab[1][self.gripper_left_name]
        
    def setup(self):
        self.sensor_left.enable(self.timestep)
        self.sensor_right.enable(self.timestep)

    def initialise(self):
        self.gripper_left.setPosition(self.open)
        self.gripper_right.setPosition(self.open)

    def update(self):
         
        currentL = self.sensor_left.getValue()
        currentR = self.sensor_right.getValue()
        currentT = currentL + currentR
        
        error = abs((self.open * 2) - currentT)
        
        if error < 0.01:
            return Status.SUCCESS
        else:
            self.gripper_left.setPosition(self.open)
            self.gripper_right.setPosition(self.open)
            return Status.RUNNING
        
    def terminate(self, new_status):
        if new_status == Status.SUCCESS:
            print(f"gripper open")