class AlpacaBroker:
    def __init__(self, paper=True):
        self.paper = paper
    def submit_multi_leg(self, legs, qty=1):
        print("BROKER STUB:", legs, qty)
