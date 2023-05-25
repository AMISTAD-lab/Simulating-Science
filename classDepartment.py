import numpy as np

class Department():
    def __init__(self, numScientists):
        self.numScientists = numScientists
    
    def __repr__(self):
        return str(self.makeScientists())

    def makeScientists(self):
        scientists = []
        for i in range(self.numScientists):
            # scientists have h-index and years left in career values
            scientists.append([np.random.randint(0, 50), np.random.randint(0, 30)])
        return scientists
