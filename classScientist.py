import numpy as np
import random
from classCell import *

class Scientist():
    def __init__(self):
        self.career = np.random.randint(1, 31)
        # hindex corresponds to where you are in your career
        self.hindex = abs(np.random.randint(20 - self.career, 35 - self.career))
        self.citcount = np.random.randint(0, 11)

    def __repr__(self):
        """String representation of Scientist"""
        return str([self.hindex, self.career, self.citcount])

    def cite(self, val):
        """decides if scientist chooses to cite another scientist in the same cell"""
        choice = np.random.randint(0, 2)
        # choice = 0 means they cite another scientist
        # choice = 1 means they don't cite 
        picked = Scientist()
        if choice == 0:
            #finding scientist with most citations
            maxcit = 0
            maxSci = Scientist()
            for sci in val:
                if sci.citcount > maxcit:
                    maxcit = sci.citcount
                    maxSci = sci
            
            #find the scientist that actually gets cited
            if maxcit < 5:
                picked = np.random.choice(val)
            else:
                picked = maxSci
            
            picked.citcount += 1
        return (self.citcount, picked.citcount)

    def probHerd(self):
        """generate the probability of the scientist following the herd 
        based on h index and career"""
        pHerd = abs((self.hindex-(31 - self.career))/(31 - self.career))
        if (self.hindex > (31 - self.career)):
            if pHerd > 1:
                pHerd = 0
            else:
                pHerd = 1 - pHerd
        else:
            if pHerd > 1:
                pHerd = 1
        return pHerd

    def chooseCell(self, board):
        """decides which cell the scientist will query according to payoff"""
        # dictionary of discovered cells' locations and payoff values
        discoveredPayoffs = {}
        maxPayoff = 0.0
        payoff = 0
        for x in board.discovered:
            discoveredPayoffs.update({board.board[x[0]][x[1]].payoff : board.board[x[0]][x[1]]})

        choice = np.random.binomial(1, self.probHerd())
        # choice = 1 --> they follow the herd
        if (choice == 1 and len(list(discoveredPayoffs.keys())) > 0) or (choice == 0 and len(board.undiscovered) == 0):
                maxPayoff = max(list(discoveredPayoffs.keys()))
                location = discoveredPayoffs.get(maxPayoff).location
        # choice = 0 --> choose randomly from undiscovered cells
        else:
            location = random.choice(board.undiscovered)

        return location

    def sciQuery(self, location, board):
        """scientist queries chosen cell"""
        self.hindex += board.board[location[0]][location[1]].cellQuery(board)
        self.career -= 1
        return self.hindex
