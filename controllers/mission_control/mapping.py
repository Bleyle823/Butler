"""Week5 controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot, Supervisor
import numpy as np
import math
from os.path import exists
from scipy import signal

from py_trees.behaviour import Behaviour
from py_trees.common import Status
from py_trees.composites import Sequence
from py_trees import logging as log_tree

def world2map(xw,yw): #addition and division for scaling points to 300x300 display
    px = round((round(299*(xw)) +1000)/6)
    py = round(((299 - round(299*yw)) +200)/6)
    return [px,py]
    
class test_for_map(Behaviour):
    def __init__(self,name):
        super(test_for_map, self).__init__(name)
   
    def update(self):
        if exists('cspace.npy'):
            print('existing cspace map found')
            return Status.SUCCESS
        else:
            print('no existing map found')
            return Status.FAILURE
    
class map_environment(Behaviour):
    def __init__(self,name,blackboard):
        super(map_environment, self).__init__(name)
        
        self.robot = blackboard.read("robot")
        self.timestep = int(self.robot.getBasicTimeStep())
        self.blackboard = blackboard
    
    def setup(self):
    
        self.display = self.robot.getDevice('display')
    
        self.gps = self.robot.getDevice('gps')
        self.compass = self.robot.getDevice('compass')
        self.lidar = self.robot.getDevice('Hokuyo URG-04LX-UG01')
        self.gps.enable(self.timestep)
        self.compass.enable(self.timestep)
        self.lidar.enable(self.timestep)
        self.lidar.enablePointCloud()

        self.fov = self.lidar.getFov()
        self.resolution = self.lidar.getHorizontalResolution()
        self.angles = np.linspace(self.fov/2,-self.fov/2,self.resolution)
        
        self.MAX_SPEED = 8
        
        self.map = np.zeros((300,300))
        kernel_width = 30
        self.kernel= np.ones((kernel_width,kernel_width))
     
    def initialise(self):
    
        self.worldX = 0 #starting position of robot
        self.worldY = 0 #starting position of robot
        self.indexi = 0
        self.lap = 0
        self.map = np.zeros((299,299))
        self.kernel= np.ones((30,30))

    def update(self):

        #gps and compass return pose and orientation
        xw = self.gps.getValues()[0]
        yw = self.gps.getValues()[1]
        worldX = xw
        worldY = yw
        theta_W=np.arctan2(self.compass.getValues()[0],self.compass.getValues()[1])
          
        # Process sensor data here. --------------------
        w_T_r = np.array([[np.cos(theta_W),-np.sin(theta_W), xw],
                      [np.sin(theta_W),np.cos(theta_W), yw],
                      [0,0,1]])            
                      
        ranges = np.array(self.lidar.getRangeImage())
        ranges[ranges == np.inf] = 1000
        
        
        X_r = np.array([(ranges*np.cos(self.angles))+0.202, #add 0.202 for lidar offset
                        ranges*np.sin(self.angles),
                        np.ones(len(self.angles))])
                        
        D = w_T_r @ X_r
        #-----------------------------------------------------
        
        #display pixels
        for index in range(80,self.resolution-80): #modify for tiago's usable results
            xw2 = D[0][index]
            yw2 = D[1][index]
            px2, py2 = world2map(xw2,yw2)
            #greyscale the probabilities
            if 0 < px2 < 300 and 0 < py2 < 300:
                self.map[px2, py2] = min(self.map[px2, py2] + 0.01, 1)
                v=int(self.map[px2, py2] * 255)
                expression_color = (v*256**2+v*256+v)
                #display
                self.display.setColor(expression_color)
                self.display.drawPixel(px2,py2)
        
        
        #print("cspace saved at cspace.npy")
        #self.hasrun = True
    
        return Status.RUNNING
        
    def terminate(self, new_status):
   
        cmap = signal.convolve2d(self.map,self.kernel,mode='same')
        cspace = cmap>0.9
        print("Map Saved!")
        np.save('cspace',cspace) 
    
