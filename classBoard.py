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
        self.rangeVal = 30
        self.randomRange = [0 for i in range(self.rangeVal)]
        [self.randomRange.append(x) for x in range(1, self.rangeVal+1)]
        # board has random payoff values in each cell, with more bias toward 0
        self.board = [[Cell(np.random.choice(self.randomRange), (i, j)) for j in range(self.cols)] for i in range(self.rows)]
        self.discovered = []
        self.undiscovered = [self.board[i][j].location for j in range(self.cols) for i in range(self.rows)]
        self.originalPays = self.getPayoffs()

    def __repr__(self):
        """string representation of Board"""
        return str(self.board)

    def getPayoffs(self):
        """returns the payoff value for each cell of the board in a way that 
        makes it easier to get a heatmap from a 2D matrix of data"""
        return [[self.board[i][j].payoff for i in range(self.cols)] for j in range(self.rows)]

    def drawBoard(self, cellsHit, numRun):
        """produces a plot of the board for a given run and saves the image"""
        data = self.getPayoffs()
        og = plt.imshow(self.originalPays, cmap="Greens", vmin=0, vmax=30)
        ogColors = og.cmap(og.norm(og.get_array()))
        plot = plt.imshow(data, cmap="Greens", vmin=0, vmax=30)
        plt.colorbar()

        for i in range(self.rows):
            for j in range(self.cols):
                cell = self.board[i][j]
                # compare to original payoff color
                plt.axhline(y = j-0.41, xmin = i/self.cols+0.019, xmax = (i+1)/self.cols+0.019, color=ogColors[j][i], linewidth=10)
                # finding the number of scientists on each cell each round
                numSciHits = 0
                if cell.location in cellsHit.keys():
                    numSciHits = len(cellsHit[cell.location])
                    # plotting the "dot" scientists
                    for x in range(1, numSciHits + 1):
                        scientist = cellsHit[cell.location][x-1]
                        starFactor = (scientist.hindex-(31 - scientist.career))/(31 - scientist.career)
                        if starFactor < 0:
                            dotSize = 5 - 5 * starFactor
                        else:
                            dotSize = 5 + 5 * starFactor
                        # generate random locations within the cell for the scientist
                        # offset of 0.5 from the way heatmap is generated
                        randX = np.random.uniform(0.1, 0.9)
                        randY = np.random.uniform(0.1, 0.9)
                        plt.plot(i+randX-0.5, j+randY-0.5,
                            marker="o", markersize=dotSize, markeredgecolor="blue",
                            markerfacecolor="blue")
                # annotating cells (phase, numHits)
                # (ex: B5 means breakthrough phase, hit 5 times)
                # add this for debugging payoffs: {f'{cell.payoff:.1f}'}
                plt.annotate(f"{cell.phase.name[0]}{cell.numHits}", xy = (i, j), xytext=(i-0.15, j+0.075),
                    fontsize=13, fontweight='bold')
        plt.savefig(f'plot{numRun}.png')
        plt.clf()
