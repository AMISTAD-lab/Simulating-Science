from phase import *

class Cell():
    def __init__(self, payoff, hidden=True, phase=Phase.experimental, numHits=0):
        self.payoff = payoff
    
    def __repr__(self):
        "string representation of Cell"
        return str(self.payoff)

    def query(self):
        self.numHits += 1
        if self.numHits > 4:
            self.phase = Phase.incremental
        elif self.numHits > 2:
            self.phase = Phase.breakthrough
        if self.phase == Phase.experimental:
            self.payoff = self.payoff/10
        elif self.phase == Phase.breakthrough:
            self.payoff = self.payoff/3
        else:
            self.payoff = self.payoff/10
        return self.payoff
