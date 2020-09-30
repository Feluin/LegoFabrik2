from camera     import *
from band       import *
from pusher     import *
from speaker    import *
from classifier import *
from enum       import Enum    
import brickpi3 
import time

BP = brickpi3.BrickPi3()                                

class Machine:

    pallet = None
    band = Band()
    pusher = Pusher()
    speaker = Speaker()
    classifier = Classifier()
    communicator = None

    def __init__(self,communicator):
        self.communicator = communicator

    def informCommunicator(self,pallet):      
        self.communicator.getNotified(pallet)           

    def calibrate(self):
        print('calibrating the machine...')
        time.sleep(3)
        self.pusher.calibrate()                         # Calibrating the pusher
        self.band.calibrate()
        print('machine calibrated')
    def shutDown(self):
        BP.reset_all()
        print('Process terminated. Shutting down...')
        self.classifier.shutDown()
        self.pusher.calibrate()  
        self.pusher.release()
        

    def sort(self, pallet):                             # Sorting method   
        self.band.moveTo('camera')                      # Moving the band to the camera for the classification of the object inside the pallet
        pallet = self.classifier.classifyObject(pallet) # Getting the pallet classified
        self.speaker.singSong(pallet.pallet_signature)  # Audio pronouncing of the kind of detected object inside the pallet
        self.band.moveTo(pallet.pallet_signature)       # Move the band to the preset position for the object inside the pallet
        time.sleep(2)
        self.pusher.rotate(pallet.pallet_signature)     # Pushing the pallet off the band
        self.band.reset(pallet.pallet_signature)        # Bringing the band to its initial position
        self.informCommunicator(pallet)                 # Bring pallet info back to communicator
        
