import numpy as np
from classScientist import *

class Department():
    def __init__(self, numScientists):
        self.numScientists = numScientists
    
    def __repr__(self):
        return str(self.makeScientists())

    def makeScientists(self):
        return [Scientist() for i in range(self.numScientists)]
