import numpy as np
import json
from PIL import Image
from classCell import *
from classBoard import *
from classScientist import *

def oneRun(board, cellsHit, numRun, starFactorWeights):
    """runs query simulation for one year"""
    for key, val in cellsHit.items():
        #more than one scientist
        if len(val) > 1:
            # randomly choose order in which scientists hit that same cell
            sciOrder = np.random.permutation(val)
            for scientist in sciOrder:
                scientist.sciQuery(key, board)
                scientist.cite(val, starFactorWeights)
        else:
            val[0].sciQuery(key, board)
    board.drawBoard(cellsHit, numRun, starFactorWeights)
    return board

def batchRun(board, numScientists, numRuns, data):
    """
    Runs the simulation for each of numRuns years.
    During each run, each scientist in the department queries the board.
    At the end, an animation of the plots of each run is generated.
    """
    weights = data["cell"]
    funding = data["fund"]
    chooseCellToFund = data["fundFactors"]
    # semi-firm parameters that you could easily change but probabily won't need to
    exp = data["exp"]["num"]
    starFactorWeights = data["star"]

    dept = [Scientist() for i in range(numScientists)]
    attrition = 0
    for j in range(numRuns):
        # keep track of which cells the scientists are hitting to check overlap
        # funding for the first year is determined randomly
        board.distributeFundingCell(chooseCellToFund, funding, exp, starFactorWeights)

        # gives which scientists are at that location
        board.cellsHit = {}
        for idx in range(len(dept)):
            scientist = dept[idx]
            # update funding decrease for each scientist each year
            scientist.funding -= funding["decrease"]
            location = scientist.chooseCell(board, weights, exp)
            if location in board.cellsHit.keys():
                board.cellsHit[location].append(scientist)
            else:
                board.cellsHit.update({location : [scientist]})
            # when one scientist ends their career, another is introduced
            if (scientist.career == 0) or (scientist.funding <= funding["minimum"]):
                # attrition is the number of scientists who left science due to lack of funding
                if (scientist.funding <= funding["minimum"]):
                    attrition += 1
                # record the data of scientists who left science
                board.sStats.append(scientist.funding)
                board.sStats.append(scientist.getStarFactor(starFactorWeights))
                board.sStats.append(scientist.citcount)
                dept.remove(scientist)
                dept.append(Scientist())
        oneRun(board, board.cellsHit, j+1, starFactorWeights)
        # print("Board with payoff values: ", oneRun(board, board.cellsHit, j+1, starFactorWeights))
        # print()

    currTotal = sum(board.flatten(board.getPayoffs()))
    print()
    print("Percentage of total payoff discovered: ", f"{((board.totalPayoff - currTotal)/board.totalPayoff)*100:.2f}")
    print()

    #animating plots
    frames = [Image.open(f'plots/plot{i+1}.png') for i in range(numRuns)]
    frame_one = frames[0]
    frame_one.save("animation.gif", format="GIF", append_images=frames,
            save_all=True, duration=500, loop=1)

    # add the scientist stats from the ten scientists at the very end
    for scientist in dept:
        board.sStats.append(scientist.funding)
        board.sStats.append(scientist.getStarFactor(starFactorWeights))
        board.sStats.append(scientist.citcount)

    # add percentage of board discovered and attrition stats
    board.bStats = [(board.totalPayoff - currTotal)/board.totalPayoff*100, 
                    attrition]

    # get cell funds and payoff of the board at the end
    for x in range(board.rows):
            for y in range(board.cols):
                cell = board.board[x][y]
                board.cStats.append(cell.location)
                board.cStats.append(cell.totalFunds)
                board.cStats.append(board.getVisPayoff(cell.location))
    return [board.bStats, board.cStats, board.sStats]

