import numpy as np
import classCell
from classCell import Cell
class Board():
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.board = [[Cell(np.random.randint(low = 0, high = 20)) for i in range(self.rows)] for j in range(self.cols)]
        # self.numSci = Scientist()

    def __repr__(self):
        """string representation of Board"""
        return str(self.board)