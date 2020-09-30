class Ramp:

    def __init__(self,id):
        self.pallets = []   # Pallets currently located on the ramp
        self.ramp_id = id   # Id of the ramp (1-6)

class Pallet:

    pallet_id    = None
    pallet_content = None   # This property contains the name of the object, which the pallet contains
    pallet_signature = None
    def __init__(self, id):
        self.pallet_id = id

class Thing:     
    def __init__(self):  
        ramp = Ramp(0)
        pallet = Pallet('#1234')
        pallet2 = Pallet('#1334')
        ramp.pallets.append(pallet)
        ramp.pallets.append(pallet2)
        print(ramp.pallets)

thing = Thing()