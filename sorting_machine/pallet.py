class Pallet:

    pallet_id    = None
    pallet_content = None   # This property contains the name of the object, which the pallet contains
    pallet_signature = None
    def __init__(self, id):
        self.pallet_id = id
        