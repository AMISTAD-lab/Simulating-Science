import numpy as np
import random
from classCell import *

class Scientist():
    def __init__(self):
        self.career = np.random.randint(0, 30)
        # hindex corresponds to where you are in your career
        self.hindex = abs(np.random.randint(20 - self.career, 35 - self.career))

    def __repr__(self):
        """String representation of Scientist"""
        return str([self.hindex, self.career])

    def sciQuery(self, board):
        # make choice to explore or follow the herd based on career status
        pHerd = abs((self.hindex-(30 - self.career))/(30 - self.career))
        if (self.hindex > (30 - self.career)):
            if pHerd > 1:
                pHerd = 0
            else:
                pHerd = 1 - pHerd
        else:
            if pHerd > 1:
                pHerd = 1
        choice = np.random.binomial(1, pHerd)
        print("pHerd: ", pHerd, ", choice: ", choice)
    
        discoveredPayoffs = {}
        maxPayoff = 0.0
        for x in board.discovered:
            discoveredPayoffs.update({board.board[x[0]][x[1]].payoff : board.board[x[0]][x[1]]})

        # choice = 1 --> they follow the herd
        if (choice == 1 and len(list(discoveredPayoffs.keys())) > 0) or (choice == 0 and len(board.undiscovered) == 0):
                print("case 1")
                maxPayoff = max(list(discoveredPayoffs.keys()))
                self.hindex += discoveredPayoffs.get(maxPayoff).cellQuery(board)
        # choice = 0 --> choose randomly from undiscovered cells
        else:
            print("case 2")
            location = random.choice(board.undiscovered)
            x = location[0]
            y = location [1]
            self.hindex += board.board[x][y].cellQuery(board)
        return self.hindex
