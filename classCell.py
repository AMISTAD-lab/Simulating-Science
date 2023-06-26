import numpy as np
import math

class Cell():
    def __init__(self, payoff, location, N, D, p):
        self.payoff = payoff
        self.location = location
        self.numHits = 0
        self.lowerx, self.upperx, self.yList = self.logiFunc(N, D)
        self.stepSize, self.slopeVals = self.setStepSize(D, p)
        self.numSciHits = 0
        self.funds = 0

    def __repr__(self):
        """string representation of Cell"""
        return str(self.payoff)

    def logiFunc(self, N, D):
        """
        model payoff extraction for each cell as a randomized logistic function
        """
        # boolean for whether we have found the lowerx and upperx
        lowSuccess = False
        highSuccess  = False

        while lowSuccess == False or highSuccess == False:
            # set steepness and center parameters for logistic function
            steepOptions = [x for x in np.arange(0.3, 7, 0.1)]
            steepness = np.random.choice(steepOptions)
            center = np.random.randint(0, 15)
            lowerx = 0
            upperx = []
            lowSuccess = False
            highSuccess = False
            for x in np.arange(0, 50, 0.01):
                y = float(1/(1 + math.pow(math.e, -steepness*(x-center))))
                # creates a boundary 0.1 above 0 and below 1 for y-val to set as upperx and lowerx
                if ((y - .01) <= 0.1) and math.floor(x) > 0:
                    lowerx = math.floor(x)
                    lowSuccess = True
                elif (.99 - y) <= 0.1:
                    upperx.append(math.ceil(x))
                    highSuccess = True
            
            xmax = min(upperx)
            #finds the y value (proportion) at given x in the logistic function
            self.incHit = float(1/(1 + math.pow(math.e, -steepness*(xmax-center))))
            self.breakHit = float(1/(1 + math.pow(math.e, -steepness*(lowerx-center))))

            # Creates a list of coordinates by D microsteps up to xmax
            yList = []
            interval = xmax/N
            for x in np.arange(0, xmax, interval/D):
                yval = float(1/(1 + math.pow(math.e, -steepness*(x-center))))
                yList += [yval]
        return lowerx, xmax, yList

    def setStepSize(self, D, p):
        """
        split the steps along the logistic function into randomized microsteps
        """
        slopeVals = {}
        # randomly generates the microstep interval
        stepSize = np.random.binomial(D*2, p, size=None)

        # calculates slopes according to stepSize
        prevY = 0
        i = 0
        while i <= self.upperx: 
            if stepSize == 0:
                slope = 0
            else:
                slope = (self.yList[i+stepSize] - prevY)/stepSize
            slopeVals[i] = slope
            prevY = self.yList[i+stepSize]
            i += 1
        return stepSize, slopeVals

    def cellQuery(self, board):
        """returns payoff for each scientist based on conditions of a cell"""
        original = self.payoff
        sciPayoff = 0.0
        self.setStepSize(self.D, self.p)
        originalPay = board.originalPays[self.location[1]][self.location[0]]
        # if we enter incremental phase, taken payoff becomes random
        if self.payoff/originalPay >= self.incHit-1:
            frac = np.random.random()
        else:
            frac = self.slopeVals[self.numHits]
        self.payoff = (1-frac) * self.payoff
        sciPayoff = frac * original
        self.numHits += 1
        return sciPayoff