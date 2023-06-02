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

    def drawBoard(self, cellsHit, numRun):
        data = self.getPayoffs()
        hm = sn.heatmap(data = data, cmap="Blues")
        
        for i in range(self.rows):
            for j in range(self.cols):
                cell = self.board[i][j]
                #finding the number of scientists on each cell each round
                numSciHits = 0
                if cell.location in cellsHit.keys():
                    numSciHits = len(cellsHit[cell.location])
                    # plotting the "dot" scientists
                    for x in range(1, numSciHits + 1):
                        hm.plot(i+(x/(1 + numSciHits)), j + 0.55,
                            marker="o", markersize=10, markeredgecolor="red",
                            markerfacecolor="red")
                #annotating cells (phase, numHits)
                #(ex: B5 means breakthrough phase, hit 5 times)
                hm.annotate(f"{cell.phase.name[0]}{cell.numHits}", xy = (j, i), xytext=(j+0.40, i+0.2),
                    fontsize=12, fontweight='bold')
                hm.annotate(f"{numSciHits, (j, i)}", xy = (j,i), xytext = (i, j+0.4), fontsize=12, fontweight='bold')
        
        plt.savefig(f'testplot{numRun}.png')
        plt.show()
