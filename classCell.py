# import numpy as np
# from phase import *
# import math

# class Cell():
#     def __init__(self, payoff, location):
#         self.payoff = payoff
#         self.location = location
#         self.hidden = True
#         self.phase = Phase.experimental
#         self.numHits = 0
#         self.lowerx, self.upperx = self.logiFunc()
#         self.numSciHits = 0

#     def __repr__(self):
#         "string representation of Cell"
#         return str(self.payoff)

#     def logiFunc(self):
#         lowSuccess = False
#         highSuccess  = False

#         while lowSuccess == False or highSuccess == False:
#             # set steepness and center parameters for logistic function
#             steepness = np.random.randint(1, 11)
#             center = np.random.randint(0, 10)
#             lowerx = 0
#             upperx = []
#             lowSuccess = False
#             highSuccess = False
#             for x in np.arange(0, 50, 0.01):
#                 y = float(1/(1 + math.pow(math.e, -steepness*(x-center))))
#                 if ((y - .01) <= 0.1) and math.floor(x) > 0:
#                     lowerx = math.floor(x)
#                     lowSuccess = True
#                     #self.phase = Phase.breakthrough
#                 elif (.99 - y) <= 0.1:
#                     upperx.append(math.ceil(x))
#                     highSuccess = True
#                     #self.phase = Phase.incremental
#         return lowerx, min(upperx)

#     def cellQuery(self, board):
#         """returns payoff for each scientist based on conditions of a cell"""
#         original = self.payoff
#         sciPayoff = 0.0

#         if self.numHits > self.upperx:
#             self.phase = Phase.incremental
#         elif self.numHits > self.lowerx:
#             self.phase = Phase.breakthrough
#             self.hidden = False
#             # "discover" the cell once it hits breakthrough phase
#             if self.location not in board.discovered:
#                 board.discovered.append(self.location)
#                 board.undiscovered.remove(self.location)
#         if self.phase == Phase.experimental:
#             self.payoff = 0.8 * self.payoff
#             sciPayoff = 0.2 * original
#         elif self.phase == Phase.breakthrough:
#             self.payoff = 0.5 * self.payoff
#             sciPayoff = 0.5 * original
#         else:
#             self.payoff = 0.8 * self.payoff
#             sciPayoff = 0.2 * original
#         self.numHits += 1
#         return sciPayoff

import numpy as np
from phase import *
import math

class Cell():
    def __init__(self, payoff, location):
        self.payoff = payoff
        self.location = location
        self.hidden = True
        self.phase = Phase.experimental
        self.numHits = 0
        self.lowerx, self.upperx, self.slopeVals = self.logiFunc(15, 10, 0.5)
        self.numSciHits = 0

    def __repr__(self):
        "string representation of Cell"
        return str(self.payoff)

    def logiFunc(self, N, D, p):
        lowSuccess = False
        highSuccess  = False

        while lowSuccess == False or highSuccess == False:
            # set steepness and center parameters for logistic function
            steepness = np.random.randint(1, 11)
            center = np.random.randint(0, 15)
            lowerx = 0
            upperx = []
            slopeVals = {}
            lowSuccess = False
            highSuccess = False
            for x in np.arange(0, 50, 0.01):
                y = float(1/(1 + math.pow(math.e, -steepness*(x-center))))
                if ((y - .01) <= 0.1) and math.floor(x) > 0:
                    lowerx = math.floor(x)
                    lowSuccess = True
                elif (.99 - y) <= 0.1:
                    upperx.append(math.ceil(x))
                    highSuccess = True
            
            xmax = min(upperx)
            #Goal: to get from x=0 to x=xmax in ksteps
            # - Chop interval into N pieces
            yList = []
            interval = xmax/N
            for x in np.arange(0, xmax, interval/D):
                yval = float(1/(1 + math.pow(math.e, -steepness*(x-center))))
                yList += [yval]
            # - for Scientist at time i, flip coin (with probability p) D times (number of microsteps)
            stepSize = np.random.binomial(D*2, p, size=None)

            #putting the slopes in a dictionary
            prevY = 0
            i = 0
            while i <= xmax: 
                if stepSize == 0:
                    slope = 0
                else:
                    slope = (yList[i+stepSize] - prevY)/stepSize
                slopeVals[i] = slope
                prevY = yList[i+stepSize]
                i += 1
        return lowerx, xmax, slopeVals

    def cellQuery(self, board):
        """returns payoff for each scientist based on conditions of a cell"""
        original = self.payoff
        sciPayoff = 0.0

        if self.numHits > self.upperx:
            self.phase = Phase.incremental
        elif self.numHits > self.lowerx:
            self.phase = Phase.breakthrough
            self.hidden = False
            # "discover" the cell once it hits breakthrough phase
            if self.location not in board.discovered:
                board.discovered.append(self.location)
                board.undiscovered.remove(self.location)
        if self.phase == Phase.incremental:
            frac = np.random.random()
        else:
            frac = self.slopeVals[self.numHits]
        self.payoff = (1-frac) * self.payoff
        sciPayoff = frac * original
        self.numHits += 1
        return sciPayoff