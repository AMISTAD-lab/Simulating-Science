import numpy as np
from phase import *
from classCell import *

class Board():
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        # board has random payoff values in each cell
        self.board = [[Cell(np.random.randint(low = 0, high = 50), (i, j)) for i in range(self.rows)] for j in range(self.cols)]
        self.discovered = []
        self.undiscovered = [self.board[i][j].location for i in range(self.rows) for j in range(self.cols)]

    def __repr__(self):
        """string representation of Board"""
        return str(self.board)
