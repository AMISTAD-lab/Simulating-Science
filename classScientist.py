import numpy as np
from classCell import *

class Scientist():
    def __init__(self):
        self.hindex = np.random.randint(0, 50)
        self.career = np.random.randint(0, 30)
    
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
            discoveredPayoffs.update({board.board[x[0]][x[1]].payoff: board.board[x[0]][x[1]]})
        if choice == 1:
            maxPayoff = max(list(discoveredPayoffs.keys()))
            discoveredPayoffs.get(maxPayoff).cellQuery(board)
            self.hindex += discoveredPayoffs.get(maxPayoff).cellQuery(board)
        else:
            # random behavior from scientists
            x = np.random.randint(0, board.rows)
            y = np.random.randint(0, board.cols)
            board.board[x][y].cellQuery(board)
            self.hindex += board.board[x][y].cellQuery(board)
        return [self.hindex, board.discovered, discoveredPayoffs, maxPayoff, discoveredPayoffs.get(maxPayoff)]
