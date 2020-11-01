from camera import *
from pallet import *
import csv
class Classifier:

    camera = None

    def __init__(self):
        self.camera = Camera()


    def classifyObject(self, pallet):                               # Method for object classification. It gets the object signature from Pixi camera and fills the pallet object with data
        signature = str(self.camera.detectObject())                 # Getting object siganature detected by Pixy
        pallet.pallet_signature = int(signature)                         # Filling pallet object with data
        pallet.pallet_content = self.readColorFromTable(signature)
        return pallet

    def readColorFromTable(self, signature):                        # Method for extracting the object name from the 'signature.csv' file
        
        with open('signatures.csv') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',' )
            for row in readCSV:
                if row[0] == signature:
                    return row[1]
    def shutDown(self):
        self.camera.shutDown()