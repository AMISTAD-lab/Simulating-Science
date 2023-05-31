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
        """returns payoff for each scientist based on conditions of a cell"""
        original = self.payoff
        sciPayoff = 0.0
        if self.numHits > 3:
            self.phase = Phase.incremental
        elif self.numHits > 1:
            self.phase = Phase.breakthrough
            self.hidden = False
            # right when it changes to breakthrough phase
            if self.numHits == 2:
                board.discovered.append(self.location)
                board.undiscovered.remove(self.location)
        if self.phase == Phase.experimental:
            self.payoff = 0.8 * self.payoff
            sciPayoff = 0.2 * original
        elif self.phase == Phase.breakthrough:
            self.payoff = 0.5 * self.payoff
            sciPayoff = 0.5 * original
        else:
            self.payoff = 0.8 * self.payoff
            sciPayoff = 0.2 * original
        self.numHits += 1
        return sciPayoff