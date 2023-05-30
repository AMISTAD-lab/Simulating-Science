import numpy as np
import random
from classCell import *

class Scientist():
    def __init__(self):
        self.hindex = np.random.randint(0, 50)
        self.career = np.random.randint(0, 10)
    
    def __repr__(self):
        return str([self.hindex, self.career])

    def sciQuery(self, board):
        # make choice to randomly explore or follow the herd
        choice = np.random.randint(0, 2)
        discoveredPayoffs = {}
        maxPayoff = 0.0
        # if they follow the herd
        for x in board.discovered:
            # find max payoff from discovered stuff
            discoveredPayoffs.update({board.board[x[0]][x[1]].payoff : board.board[x[0]][x[1]]})
        if choice == 1 and len(list(discoveredPayoffs.keys())) > 0:
                maxPayoff = max(list(discoveredPayoffs.keys()))
                self.hindex += discoveredPayoffs.get(maxPayoff).cellQuery(board)
        else:
            # random behavior from scientists
            location = random.choice(board.undiscovered)
            x = location[0]
            y = location [1]
            self.hindex += board.board[x][y].cellQuery(board)
        return self.hindex
