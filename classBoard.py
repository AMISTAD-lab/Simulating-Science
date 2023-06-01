import seaborn as sn
import matplotlib.pyplot as plt
import numpy as np
import math
from phase import *
from classCell import *

class Board():
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        # creates biased random number generator with 50% chance of being 0
        rangeVal = 30
        self.randomRange = [0 for i in range(rangeVal)]
        [self.randomRange.append(x) for x in range(1, rangeVal+1)]
        # board has random payoff values in each cell, with more bias toward 0
        self.board = [[Cell(np.random.choice(self.randomRange), (i, j)) for i in range(self.rows)] for j in range(self.cols)]
        self.discovered = []
        self.undiscovered = [self.board[i][j].location for i in range(self.rows) for j in range(self.cols)]

    def __repr__(self):
        """string representation of Board"""
        return str(self.board)

    def getPayoffs(self):
        return [[self.board[i][j].payoff for i in range(self.rows)] for j in range(self.cols)]

    def drawBoard(self, cellsHit):
        data = self.getPayoffs()
        hm = sn.heatmap(data = data, cmap="Blues")
        for i in range(self.rows):
            for j in range(self.cols):
                cell = self.board[i][j]
                numSciHits = 0
                if cell.location in cellsHit.keys():
                    numSciHits = len(cellsHit[cell.location])
                hm.annotate(f"{cell.phase.name[0]}{cell.numHits}{numSciHits}", xy=(i, j), xytext=(i+0.40, j+0.5),
                    fontsize=12, fontweight='bold')
        plt.show()
