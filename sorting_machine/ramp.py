from pallet import *
class Ramp:

    def __init__(self,id):
        self.pallets = []   # Pallets currently located on the ramp
        self.ramp_id = id   # Id of the ramp (1-6)