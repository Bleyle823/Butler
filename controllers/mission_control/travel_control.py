# travel moves the robot along a predetermined waypoint path from the blackboard

from controller import Robot, Supervisor
import numpy as np
from scipy import signal
from heapq import heapify, heappush, heappop
from collections import defaultdict
import math

from py_trees.behaviour import Behaviour
from py_trees.common import Status
from py_trees.composites import Sequence

def map2world(xm,ym):
    wx = round((round(299*(xm)) +1000)/6)
    wy = round(((299 - round(299*ym)) +200)/6)
    #print(f"{wx} {wy}")
    return [wx,wy]
    
def world2map(xw,yw): #addition and division for scaling points to 300x300 display
    px = (6*xw-1000)/299
    py = (499 - 6*yw)/299
    return (px,py)
    
def wheel_speed(value, limit):
    if not math.isfinite(value):
        return 0.0
    if value > limit:
        return limit
    if value < -limit:
        return -limit
    return value

def wrap_angle(angle):
    if not math.isfinite(angle):
        return 0.0
    while angle > math.pi:
        angle -= 2 * math.pi
    while angle < -math.pi:
        angle += 2 * math.pi
    return angle

def getNeighbors(tuple1,map):
    neighbors = []
    for move in ((0,1),(0,-1),(1,0),(-1,0),(1,1),(-1,1),(-1,-1),(1,-1)): #8 neighborhood (means can move diagonally too)
        candidate = (tuple1[0]+move[0],tuple1[1]+move[1])
        if (candidate[0]>=0 and candidate[0]<len(map) and candidate[1]>=0 and candidate[1]<len(map[0]) and map[candidate[0]][candidate[1]]<1):
            neighbors.append((math.sqrt(move[0]**2 + move[1]**2),candidate))
    return neighbors
    
class move(Behaviour):
    def __init__(self,name,blackboard):
        super(move, self).__init__(name)
        self.robot = blackboard.read("robot")
        self.timestep = int(self.robot.getBasicTimeStep())
        self.blackboard = blackboard
        
    def setup(self):
    
        #self.marker = self.robot.getFromDef("marker").getField("translation")
        self.gps = self.robot.getDevice('gps')
        self.compass = self.robot.getDevice('compass')
        self.gps.enable(self.timestep)
        self.compass.enable(self.timestep)

        #set up wheel motors
        self.leftmotor = self.robot.getDevice('wheel_left_joint')
        self.rightmotor = self.robot.getDevice('wheel_right_joint')
        
        self.leftmotor.setVelocity(0)
        self.rightmotor.setVelocity(0)
        
    def initialise(self):
        
        self.leftmotor.setPosition(float('inf'))
        self.rightmotor.setPosition(float('inf'))
        
        #the path to follow
        self.WP = self.blackboard.read('WP')
        print("following path...")
        
        self.worldX = self.gps.getValues()[0] #starting position of robot
        self.worldY = self.gps.getValues()[1] #starting position of robot
        self.indexi = 0
        
        self.MAX_SPEED = 8
    
    def update(self):
        #gps and compass return pose and orientation
        xw = self.gps.getValues()[0]
        yw = self.gps.getValues()[1]
        worldX = xw
        worldY = yw
        theta_W=np.arctan2(self.compass.getValues()[0],self.compass.getValues()[1])
        
        #set appropriate waypoint
        #self.marker.setSFVec3f([*self.WP[self.indexi],0])
        
        #distance and orientation calcs
        rho = np.sqrt(((self.WP[self.indexi][0]-xw)**2)+((self.WP[self.indexi][1]-yw)**2)) #distance to waypoint
        theta_P=np.arctan2(self.WP[self.indexi][1]-yw,self.WP[self.indexi][0]-xw)
        theta_F = theta_P-theta_W #angle to waypoint
        
        theta_F = wrap_angle(theta_F)
        angle1 = math.degrees(theta_F)
        
        #waypoint chaser
        if (rho < 0.3):  #if within 30cm
            self.indexi = self.indexi + 1 #traverse CW
            if self.indexi >= len(self.WP):
                print('Reached Goal!')
                self.leftmotor.setVelocity(0)
                self.rightmotor.setVelocity(0)
                return Status.SUCCESS
                    
        p1 = 3
        p2 = 2.5
        speed_boost = 1
        phiLdot = (-theta_F*p1 + rho*p2)*speed_boost
        phiRdot = (theta_F*p1 + rho*p2)*speed_boost
        
        self.leftmotor.setVelocity(wheel_speed(phiLdot, self.MAX_SPEED))
        self.rightmotor.setVelocity(wheel_speed(phiRdot, self.MAX_SPEED))

        return Status.RUNNING
        
    def terminate(self, new_status):
        self.leftmotor.setVelocity(0)
        self.rightmotor.setVelocity(0)
        
class back_up(Behaviour):
    def __init__(self,name,blackboard):
        super(back_up, self).__init__(name)
        self.robot = blackboard.read("robot")
        self.timestep = int(self.robot.getBasicTimeStep())
        self.blackboard = blackboard
        
    def setup(self):

        #set up wheel motors
        self.leftmotor = self.robot.getDevice('wheel_left_joint')
        self.rightmotor = self.robot.getDevice('wheel_right_joint')
        self.leftmotor_sensor = self.robot.getDevice('wheel_left_joint_sensor')
        self.rightmotor_sensor = self.robot.getDevice('wheel_right_joint_sensor')
        
    def initialise(self):
        
        self.wait_start = self.robot.getTime()
        self.leftmotor_sensor.enable(self.timestep)
        self.rightmotor_sensor.enable(self.timestep)
        self.curL0 = self.leftmotor_sensor.getValue()
        self.curR0 = self.rightmotor_sensor.getValue()
        
        self.leftmotor.setVelocity(0)
        self.rightmotor.setVelocity(0)
        
    def update(self):
        curL = self.leftmotor_sensor.getValue() - self.curL0
        curR = self.rightmotor_sensor.getValue() - self.curR0
        
        if (self.robot.getTime() - self.wait_start) < 2:
            return Status.RUNNING
        elif (abs(curL+curR)-5)<0.5:
            self.leftmotor.setVelocity(-2)
            self.rightmotor.setVelocity(-2)
            return Status.RUNNING
        else:
            return Status.SUCCESS

    def terminate(self, new_status):
        if new_status == Status.SUCCESS:
            self.leftmotor.setVelocity(0)
            self.rightmotor.setVelocity(0)
            
class route(Behaviour):
    def __init__(self,name,blackboard,goal):
        super(route, self).__init__(name)
        self.robot = blackboard.read("robot")
        self.timestep = int(self.robot.getBasicTimeStep())
        self.blackboard = blackboard
        self.goal = goal
        
    def setup(self):
    
        self.display = self.robot.getDevice('display')
        self.gps = self.robot.getDevice('gps')
        self.gps.enable(self.timestep)
        self.leftmotor = self.robot.getDevice('wheel_left_joint')
        self.rightmotor = self.robot.getDevice('wheel_right_joint')
        self.leftmotor.setPosition(float('inf'))
        self.rightmotor.setPosition(float('inf'))

    def initialise(self):
    
        self.leftmotor.setVelocity(0)
        self.rightmotor.setVelocity(0)
        
        self.map_file = np.load('cspace.npy')
        self.rows = self.map_file.shape[1]
        self.cols = self.map_file.shape[0]
        
        xw1 = self.gps.getValues()[0]
        yw1 = self.gps.getValues()[1]

        self.start_node = tuple(round(x) for x in map2world(xw1,yw1)) 
        
        #----------------------------------------------
        print("calculating route for: ")
        print("start node", self.start_node)
        print("goal node", self.goal)
        #----------------------------------------------
        
        self.distances=defaultdict(lambda:float('inf'))
        self.distances[self.start_node]=0
        self.parent = {}
        
        self.queue = [(0,self.start_node)]
        heapify(self.queue)
        self.visited = {self.start_node}
        
        #Draw the map----------------------------
        self.display.setColor(0x0FFFFFF) 
        for i in range(self.map_file.shape[0]):  # Rows
            for j in range(self.map_file.shape[1]):  # Columns
                # If it's an obstacle (1), set it to black, otherwise white
                if self.map_file[i, j] == 1:
                    self.display.drawPixel(i, j)
        #---------------------------------------------
    
    def update(self):
    
        if not self.queue:
            print("No path exists!")
            return Status.FAILURE
            
        (currentdist,node) = heappop(self.queue) #pop(0) uses first in first out
        self.visited.add(node)
        for (costnton,neighbor) in getNeighbors(node,self.map_file):
            if neighbor not in self.visited:
                dist = np.sqrt((self.goal[0]-neighbor[0])**2+(self.goal[1]-neighbor[1])**2)
                newcost = dist + costnton
                if newcost < self.distances[neighbor]:
                    self.distances[neighbor] = newcost
                    heappush(self.queue,(newcost,neighbor))
                    self.parent[neighbor] = node
                    if neighbor == self.goal:
                        print("path found", flush=True)
                        return Status.SUCCESS
        return Status.RUNNING
        
    def terminate(self, new_status):
        if new_status == Status.SUCCESS:
            
            #the path-----------------------------------------
            key = self.goal 
            path = []
            
            seen = set()
            while key in self.parent.keys() and key not in seen:
                seen.add(key)
                key = self.parent[key]
                path.insert(0,key)
            path.append(self.goal)
            
            #make a WP list out of the path --------------------------------------
            WP = []
            for p in range(0,len(path)): 
                if (p%10 == 0) or p == len(path): #split the optimal path into waypoints
                #make sure the goal is in the waypoints
                    #entry1,entry2 = world2map(path[p][0],path[p][1])
                    #WP.append((entry1,entry2))
                    WP.append(world2map(path[p][0],path[p][1]))
            self.blackboard.write('WP',WP)
            #print(WP)
            #plot final path-----------------------------------------------------
            self.display.setColor(0x0FFFF0) 
            for point in path: #modify for tiago's usable results
                xw2 = point[0]
                yw2 = point[1]
                #draw path
                self.display.drawPixel(xw2,yw2) 
            #---------------------------------------------------------------------
                   
class get_in_position(Behaviour): #places gripper around object
    def __init__(self,name,blackboard,object_name=None,zone=None):
    
        self.object_name = object_name
        
        super(get_in_position, self).__init__(name)
        self.robot = blackboard.read("robot")
        self.timestep = int(self.robot.getBasicTimeStep())
        self.blackboard = blackboard
        self.zone = zone

    def setup(self):

        self.gps = self.robot.getDevice('gps')
        self.compass = self.robot.getDevice('compass')
        self.gps.enable(self.timestep)
        self.compass.enable(self.timestep)
        
        #set up wheel motors
        self.leftmotor = self.robot.getDevice('wheel_left_joint')
        self.rightmotor = self.robot.getDevice('wheel_right_joint')
        
        self.leftmotor.setVelocity(0)
        self.rightmotor.setVelocity(0)
        
        self.MAX_SPEED = 3

    def initialise(self):
    
        if self.object_name:
            self.full_locs = self.blackboard.read("object_location")
            self.all_obj = self.blackboard.read("object_location")[self.object_name]
            self.location = self.all_obj[0]
        else:
            self.location = self.blackboard.read('drop_zones')[self.zone]
        print(self.location) #- DEBUGGING
            
        self.leftmotor.setVelocity(0)
        self.rightmotor.setVelocity(0)
        
        xw = self.gps.getValues()[0]
        yw = self.gps.getValues()[1]
        
        #half = np.array([(self.object[0]-xw)/2,(self.object[1]-yw)/2])

    def update(self):
    
        self.leftmotor.setVelocity(0)
        self.rightmotor.setVelocity(0)
        
        xw = self.gps.getValues()[0]
        yw = self.gps.getValues()[1]
        worldX = xw
        worldY = yw
        theta_W=np.arctan2(self.compass.getValues()[0],self.compass.getValues()[1])
        
        #set appropriate waypoint
        #self.marker.setSFVec3f([*self.WP[self.indexi],0])
        
        #distance and orientation calcs
        rho = np.sqrt(((self.location[0]-xw)**2)+((self.location[1]-yw)**2)) #distance to waypoint
        theta_P=np.arctan2(self.location[1]-yw,self.location[0]-xw)
        theta_F = theta_P-theta_W #angle to waypoint
        #print(theta_F)
        theta_F = wrap_angle(theta_F)
        angle1 = math.degrees(theta_F)
                  
        p1 = 3
        p2 = 2.5
        phiLdot = -theta_F*p1 + rho*p2
        phiRdot = theta_F*p1 + rho*p2
        
        #print(theta_F)
        #if (abs(angle1) < 0.3) & (rho > 1.12): #THEN, DRIVE INTO POSITION (arm is 1.15 long)
        #    self.leftmotor.setVelocity(max(min(phiLdot*2,1.2),-1))
        #    self.rightmotor.setVelocity(max(min(phiRdot*2,1.2),-1))
        #    return Status.RUNNING
        #print(rho)
        if (abs(angle1) < 0.24) & (rho > 1.13): #THEN, DRIVE INTO POSITION (arm is 1.15 long)
            self.leftmotor.setVelocity(wheel_speed(phiLdot*2, 1.1))
            self.rightmotor.setVelocity(wheel_speed(phiRdot*2, 1.1))
            return Status.RUNNING
        elif abs(angle1) > 0.24: #FIRST, ROTATE TO THE OBJECT
            rotation_speed = max(min(abs(theta_F)*3, self.MAX_SPEED/3), 0.1)
            if abs(angle1) > 35:
                rotation_speed = 3
            direction = np.sign(theta_F) if math.isfinite(theta_F) else 0.0
            
            left = (-direction * rotation_speed)
            right = (direction * rotation_speed)

            self.leftmotor.setVelocity(wheel_speed(left, self.MAX_SPEED))
            self.rightmotor.setVelocity(wheel_speed(right, self.MAX_SPEED))
            return Status.RUNNING
        else:
            self.leftmotor.setVelocity(0)
            self.rightmotor.setVelocity(0)
            return Status.SUCCESS
         
    def terminate(self, new_status):
        if new_status == Status.SUCCESS:
            if self.object_name:
                if len(self.all_obj)>1:
                    remaining_objects = self.all_obj[1::]
                    print(len(self.all_obj[1::]), self.object_name, "(s) remaining after this one")
                    self.full_locs[self.object_name] = remaining_objects
                    self.blackboard.write("object_location",self.full_locs)
                    print(self.blackboard.read("object_location"))
                else:
                    print("No", self.object_name, "(s) remaining after this one")
                    self.full_locs[self.object_name] = None
                    self.blackboard.write("object_location",self.full_locs)
                print('remaining objects and locations: ', self.full_locs)
            print("In position")
            
class rotate_to_face(Behaviour): #places gripper around object
    def __init__(self,name,blackboard,object_name=None,zone=None):
    
        self.object_name = object_name
        
        super(rotate_to_face, self).__init__(name)
        self.robot = blackboard.read("robot")
        self.timestep = int(self.robot.getBasicTimeStep())
        self.blackboard = blackboard
        self.zone = zone

    def setup(self):

        self.gps = self.robot.getDevice('gps')
        self.compass = self.robot.getDevice('compass')
        self.gps.enable(self.timestep)
        self.compass.enable(self.timestep)
        
        #set up wheel motors
        self.leftmotor = self.robot.getDevice('wheel_left_joint')
        self.rightmotor = self.robot.getDevice('wheel_right_joint')
        
        self.leftmotor.setVelocity(0)
        self.rightmotor.setVelocity(0)
        
        self.MAX_SPEED = 2

    def initialise(self):
    
        if self.object_name:
            self.all_obj = self.blackboard.read("object_location")[self.object_name]
            self.location = self.all_obj[0]
        else:
            self.location = self.blackboard.read('drop_zones')[self.zone]
        print(self.location) #- DEBUGGING
            
        self.leftmotor.setVelocity(0)
        self.rightmotor.setVelocity(0)
        
        xw = self.gps.getValues()[0]
        yw = self.gps.getValues()[1]
        
        if self.zone != None: self.dist = 1.2
        else: self.dist = 1.6
        #half = np.array([(self.object[0]-xw)/2,(self.object[1]-yw)/2])

    def update(self):
    
        self.leftmotor.setVelocity(0)
        self.rightmotor.setVelocity(0)
        
        xw = self.gps.getValues()[0]
        yw = self.gps.getValues()[1]
        worldX = xw
        worldY = yw
        theta_W=np.arctan2(self.compass.getValues()[0],self.compass.getValues()[1])
        
        #set appropriate waypoint
        #self.marker.setSFVec3f([*self.WP[self.indexi],0])
        
        #distance and orientation calcs
        rho = np.sqrt(((self.location[0]-xw)**2)+((self.location[1]-yw)**2)) #distance to waypoint
        theta_P=np.arctan2(self.location[1]-yw,self.location[0]-xw)
        theta_F = theta_P-theta_W #angle to waypoint
        #print(theta_F)
        
        theta_F = wrap_angle(theta_F)
        angle1 = math.degrees(theta_F)
                  
        p1 = 3
        p2 = 2.5
        phiLdot = -theta_F*p1 + rho*p2
        phiRdot = theta_F*p1 + rho*p2
        
        #print(self.dist)
        if (abs(angle1) < 0.25) & (rho < self.dist): #FACE AND BACK UP
            backup = wheel_speed(min(-rho, -1), self.MAX_SPEED)
            self.leftmotor.setVelocity(backup)
            self.rightmotor.setVelocity(backup)
            return Status.RUNNING
        elif abs(angle1) > 0.25: #FIRST, ROTATE TO THE OBJECT
            rotation_speed = max(min(abs(theta_F)*3, self.MAX_SPEED/3), 0.1)
            if abs(angle1) > 35:
                rotation_speed = 3
            direction = np.sign(theta_F) if math.isfinite(theta_F) else 0.0
            
            left = (-direction * rotation_speed)
            right = (direction * rotation_speed)

            self.leftmotor.setVelocity(wheel_speed(left, self.MAX_SPEED))
            self.rightmotor.setVelocity(wheel_speed(right, self.MAX_SPEED))
            return Status.RUNNING
        else:
            self.leftmotor.setVelocity(0)
            self.rightmotor.setVelocity(0)
            return Status.SUCCESS
         
    def terminate(self, new_status):
        if new_status == Status.SUCCESS:
            pass