import numpy as np
import random
from classCell import *

class Scientist():
    def __init__(self):
        self.career = np.random.randint(1, 31)
        # hindex corresponds to where you are in your career
        self.hindex = abs(np.random.randint(20 - self.career, 35 - self.career))

    def __repr__(self):
        """String representation of Scientist"""
        return str([self.hindex, self.career])

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
