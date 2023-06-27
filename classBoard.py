import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from classCell import *

class Board():
    def __init__(self, rows, cols, probzero, N, D, p):
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
        # we also pass in parameters N, D, p to split the extraction of the payoff
        # into randomized microsteps with probability p
        self.board = [[Cell(np.random.choice(self.randomRange), (i, j), N, D, p) for j in range(self.cols)] for i in range(self.rows)]
        self.originalPays = self.getPayoffs()
        self.totalPayoff = sum(self.flatten(self.originalPays))
        #dictionary of cell location with scientists currently querying it
        self.cellsHit = {}

    def __repr__(self):
        """string representation of Board"""
        return str(self.board)

    def getPayoffs(self):
        """returns the payoff value for each cell of the board in a way that 
        makes it easier to get a heatmap from a 2D matrix of data"""
        # note that the x and y coordinates were flipped to make the heatmap
        return [[self.board[i][j].payoff for i in range(self.cols)] for j in range(self.rows)]

    def getVisPayoff(self, location):
        '''
        returns the payoff that has been extracted from given cell location;
        this is what is visible to the scientists
        '''
        return (self.originalPays[location[1]][location[0]] - self.board[location[0]][location[1]].payoff)

    def flatten(self, matrix):
        """turns a 2D matrix into a 1D list"""
        return [matrix[i][j] for j in range(len(matrix[0])) for i in range(len(matrix))]

    def distributeFundingSci(self, cell, dept, cellFunding, starFactorWeights):
        """
        distribute the funding allotted for each cell to the scientists in the cell
        """
        denominator = 0
        probabilities = np.zeros_like(dept)
        for sci in dept:
            star = sci.getStarFactor(starFactorWeights)
            # ensure numbers are in reasonable range
            if star <= -1:
                star = 1/abs(star)
            elif star < 1:
                star = 1
            denominator += np.exp(star)

        for i in range(len(dept)):
            star = dept[i].getStarFactor(starFactorWeights)
            if star <= -1:
                star = 1/abs(star)
            elif star < 1:
                star = 1
            numerator = np.exp(star)
            
            probabilities[i] = numerator / denominator
            # distribute funding based on starFactor for each scientist compared to whole department
            dept[i].funding += probabilities[i] * cellFunding

        return [sci.funding for sci in dept]

    def distributeFundingCell(self, chooseCellToFund, funding, exp, starFactorWeights):
        """distributes funding to each cell based on input weights"""
        # Calculate the probabilities for each cell
        probabilities = np.random.rand(self.rows, self.cols)
        denominator = 0
        for x in range(self.rows):
            for y in range(self.cols):
                cell = self.board[x][y]
                #find the average of scientists' starFactors in this cell
                starSum = 0
                avgStarSum = 0
                if cell.location in self.cellsHit.keys():
                    for sci in self.cellsHit[cell.location]:
                        starSum += sci.getStarFactor(starFactorWeights)
                    avgStarSum = starSum/cell.numSciHits

                # account for the fact that starFactor can be negative
                if avgStarSum <= -1:
                    starWeight = chooseCellToFund["starFactor"] * 1/abs(avgStarSum)
                elif avgStarSum >= 1:
                    starWeight = chooseCellToFund["starFactor"] * (avgStarSum)
                else:
                    starWeight = chooseCellToFund["starFactor"]
                #calculates the rest of the weights
                visWeight = chooseCellToFund["visPayoff"] * (self.getVisPayoff(cell.location))
                numHitsWeight = chooseCellToFund["numHits"] * (cell.numHits)
                recentHitsWeight = chooseCellToFund["numSciHits"] * (cell.numSciHits)

                denominator += (visWeight + starWeight + numHitsWeight + recentHitsWeight) ** exp
        
        # generate random probabilities if denominator is 0
        if denominator == 0:
            sumProbs = sum(self.flatten(probabilities))
            probabilities = [[probabilities[i][j] / sumProbs for j in range(len(probabilities[0]))] for i in range(len(probabilities))]
            for i in range(len(probabilities)):
                for j in range(len(probabilities[0])):
                    #fund cell and then scientist based on probabilities
                    cell = self.board[i][j]
                    cell.funds = probabilities[i][j] * funding["total"]
                    if cell.location in self.cellsHit.keys():
                        self.distributeFundingSci(cell, self.cellsHit[cell.location], cell.funds, starFactorWeights)
            return probabilities

        for j in range(self.rows):
            for k in range(self.cols):
                cell = self.board[j][k]
                #find the average of scientists' starFactors in this cell
                starSum = 0
                avgStarSum = 0
                if cell.location in self.cellsHit.keys():
                    for sci in self.cellsHit[cell.location]:
                        starSum += sci.getStarFactor(starFactorWeights)
                    avgStarSum = starSum/cell.numSciHits

                # account for the fact that starFactor can be negative
                if avgStarSum <= -1:
                    starWeight = chooseCellToFund["starFactor"] * 1/abs(avgStarSum)
                elif avgStarSum >= 1:
                    starWeight = chooseCellToFund["starFactor"] * (avgStarSum)
                else:
                    starWeight = chooseCellToFund["starFactor"]

                visWeight = chooseCellToFund["visPayoff"] * (self.getVisPayoff(cell.location))
                numHitsWeight = chooseCellToFund["numHits"] * (cell.numHits)
                recentHitsWeight = chooseCellToFund["numSciHits"] * (cell.numSciHits)

                numerator = (visWeight + starWeight + numHitsWeight + recentHitsWeight) ** exp
                probabilities[j][k] = numerator / denominator

                #fund cell and then scientist based on probabilities
                cell.funds = probabilities[j][k] * funding["total"]
                if cell.location in self.cellsHit.keys():
                    self.distributeFundingSci(cell, self.cellsHit[cell.location], cell.funds, starFactorWeights)
        return probabilities

    def drawBoard(self, cellsHit, numRun, starFactorWeights):
        """produces a plot of the board for a given run and saves the image"""
        data = self.getPayoffs()
        plot = plt.imshow(data, cmap="Greens", vmin=0, vmax=30)
        plotColors = plot.cmap(plot.norm(plot.get_array()))
        original = plt.imshow(self.originalPays, cmap="Greens", vmin=0, vmax=30)
        plt.colorbar()
        plt.axis("off")

        for i in range(self.rows):
            for j in range(self.cols):
                cell = self.board[i][j]
                # compare to original payoff color
                # we want at least some of the original payoff to show
                if self.originalPays[j][i] != 0:
                    if cell.payoff/self.originalPays[j][i] < 0.1:
                        rect=patches.Rectangle((i-0.5,j-0.51),
                                1, 0.9,
                                fill=True,
                                color=plotColors[j][i],
                                linewidth=0.4)
                    else:
                        rect=patches.Rectangle((i-0.5,j-0.51),
                                1, (1 - (cell.payoff/self.originalPays[j][i])),
                                fill=True,
                                color=plotColors[j][i],
                                linewidth=0.4)
                    plt.gca().add_patch(rect)
                # finding the number of scientists on each cell each round
                cell.numSciHits = 0
                if cell.location in cellsHit.keys():
                    cell.numSciHits = len(cellsHit[cell.location])
                    # plotting the "dot" scientists
                    for x in range(1, cell.numSciHits + 1):
                        scientist = cellsHit[cell.location][x-1]
                        starFactor = scientist.getStarFactor(starFactorWeights)
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
                        # uncomment the following code to display starFactor along with each scientist's dot
                        # plt.annotate(f"{starFactor:.1f}", xy = (i+randX-0.5, j+randY-0.5), xytext=(i+randX-0.5, j+randY-0.5),
                        #     fontsize=5, fontweight='bold')
                # uncomment and change the following code to display cell values on image
                # plt.annotate(f"{cell.funds:.2f}", xy = (i, j), xytext=(i-0.15, j+0.075),
                #     fontsize=13, fontweight='bold')
                gridlines = patches.Rectangle((i-0.5,j-0.5),
                                1, 1,
                                fill=False,
                                color="k",
                                linewidth=2)
                plt.gca().add_patch(gridlines)
        # finish plotting gridlines on the edges of the board
        plt.axhline(self.rows-0.5, linewidth=4, color="k")
        plt.axvline(-0.5, ymax=0.94, linewidth=4, color="k")
        plt.axvline(self.cols-0.5, ymax=0.94, linewidth=4, color="k")

        plt.savefig(f'plots/plot{numRun}.png')
        plt.clf()
        plt.cla()
        plt.close()