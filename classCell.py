from phase import *

class Cell():
    def __init__(self, payoff, location):
        self.payoff = payoff
        self.location = location
        self.hidden = True
        self.phase = Phase.experimental
        self.numHits = 0

    def __repr__(self):
        "string representation of Cell"
        return str(self.payoff)

    def cellQuery(self, board):
        sciPayoff = 0.0
        self.numHits += 1
        if self.numHits > 3:
            self.phase = Phase.incremental
        elif self.numHits > 1:
            self.phase = Phase.breakthrough
            self.hidden = False
            board.discovered.append(self.location)
        if self.phase == Phase.experimental:
            self.payoff = 0.8 * self.payoff
            sciPayoff = 0.2 * self.payoff
        elif self.phase == Phase.breakthrough:
            self.payoff = 0.5 * self.payoff
            sciPayoff = 0.5 * self.payoff
        else:
            self.payoff = 0.8 * self.payoff
            sciPayoff = 0.2 * self.payoff
        return sciPayoff