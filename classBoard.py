import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from phase import *
from classCell import *

class Board():
    def __init__(self, rows, cols, probzero):
        self.rows = rows
        self.cols = cols
        self.probzero = probzero

        #Max payoff value
        self.rangeVal = 30

        #adds # of desired zeros
        self.randomRange = [0 for i in range(probzero)]

        #this makes 1,2,3...30 (payoff values)
        [self.randomRange.append(x) for x in range(1, self.rangeVal+1)]

        #shuffles the array (so its not just  [0,0,1,2] but random [2,0,1,0])
        np.random.shuffle(self.randomRange)

        # board has random payoff values in each cell
        self.board = [[Cell(np.random.choice(self.randomRange), (i, j)) for j in range(self.cols)] for i in range(self.rows)]
        self.discovered = []
        self.undiscovered = [self.board[i][j].location for j in range(self.cols) for i in range(self.rows)]
        self.originalPays = self.getPayoffs()
        self.totalPayoff = sum(self.flatten(self.originalPays))

    def __repr__(self):
        """string representation of Board"""
        return str(self.board)

    def getPayoffs(self):
        """returns the payoff value for each cell of the board in a way that 
        makes it easier to get a heatmap from a 2D matrix of data"""
        return [[self.board[i][j].payoff for i in range(self.cols)] for j in range(self.rows)]

    def flatten(self, matrix):
        """turns a 2D matrix into a 1D list"""
        return [matrix[i][j] for j in range(len(matrix[0])) for i in range(len(matrix))]

    def drawBoard(self, cellsHit, numRun):
        """produces a plot of the board for a given run and saves the image"""
        data = self.getPayoffs()
        plot = plt.imshow(data, cmap="Greens", vmin=0, vmax=30)
        plotColors = plot.cmap(plot.norm(plot.get_array()))
        original = plt.imshow(self.originalPays, cmap="Greens", vmin=0, vmax=30)
        plt.colorbar()
        plt.axis("off")
        # fig, ax = plt.subplots()

        for i in range(self.rows):
            for j in range(self.cols):
                cell = self.board[i][j]

                # compare to original payoff color
                
                # we want at least some of the original payoff to show
                if self.originalPays[j][i] != 0:
                    if cell.payoff/self.originalPays[j][i] < 0.1:
                        rect=patches.Rectangle((i-0.5,j-0.5),
                                1, 0.9,
                                fill=True,
                                color=plotColors[j][i])
                    else:
                        rect=patches.Rectangle((i-0.5,j-0.5),
                                1, (1 - (cell.payoff/self.originalPays[j][i])),
                                fill=True,
                                color=plotColors[j][i])
                    plt.gca().add_patch(rect)
                # finding the number of scientists on each cell each round
                cell.numSciHits = 0
                if cell.location in cellsHit.keys():
                    cell.numSciHits = len(cellsHit[cell.location])
                    # plotting the "dot" scientists
                    for x in range(1, cell.numSciHits + 1):
                        scientist = cellsHit[cell.location][x-1]
                        starFactor = scientist.getStarFactor()
                        if starFactor < 0:
                            if (7 - 7 * abs(starFactor)) < 3:
                                dotSize = 3
                            else:
                                dotSize = 7 - 7 * abs(starFactor)
                        else:
                            if (starFactor) >= 1:
                                dotSize = 14
                            else:
                                dotSize = 7 + 7 * (starFactor)
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
        plt.savefig(f'plots/plot{numRun}.png')
        plt.clf()
        plt.cla()
        plt.close()
        # fig.clf()
