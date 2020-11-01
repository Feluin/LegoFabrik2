from __future__ import print_function
from __future__ import division

import time 
import pixy
from ctypes import *
from pixy import *

class Blocks (Structure):                               # Defining Pixi Block structure
  _fields_ = [ ("m_signature", c_uint),
    ("m_x", c_uint),
    ("m_y", c_uint),
    ("m_width", c_uint),
    ("m_height", c_uint),
    ("m_angle", c_uint),
    ("m_index", c_uint),
    ("m_age", c_uint) ]

class Camera:

    def __init__(self):
        #print("testClassifier")
        pixy.init()
        #pixy.change_prog ("color_connected_components") # Selection of the Pixi object detection program


    
    def detectObject(self):                             # Method for detection of the object inside a pallet. The method returns the first detected object

        blocks = BlockArray(1)
        objectFound = False
        pixy.set_lamp (1, 0)                            # Turning the pixi light on
        
        while objectFound == False:
            count = pixy.ccc_get_blocks (1, blocks)
            
            if count > 0:
                objectFound = True
                print('Object Detected: Signature %d' % blocks[0].m_signature)
                
        time.sleep(2)
        pixy.set_lamp (0, 0)                            # Turning the pixi light off
        return blocks[0].m_signature

    def shutDown(self):                                 # Method for preparation for shutDown
        pixy.set_lamp (0, 0)                            # Turning the pixi light off


