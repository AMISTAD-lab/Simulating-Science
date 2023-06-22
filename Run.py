from PIL import Image
import numpy as np
from classCell import *
from classBoard import *
from classScientist import *

weights = {
    "citation" : 0.5, 
    "impact" : 0.5,
    "exploration" : 0.5,
    "funding" : 0.5
}

funding = {
    "total" : 100,
    "decrease" : 1,
    "replenishTime" : 5,
    "minimum" : 10
}

chooseCellToFund = {
    "visPayoff" : 0.5,
    "starFactor" : 0.5,
    "numHits" : 0.5,
    "numSciHits" : 0.5
}

def oneRun(board, cellsHit, numRun):
    """runs query simulation for one year"""
    for key, val in cellsHit.items():
        if len(val) > 1:
            # randomly choose order in which scientists hit that same cell
            sciOrder = np.random.permutation(val)
            for scientist in sciOrder:
                scientist.sciQuery(key, board)
                scientist.cite(val)
        else:
            val[0].sciQuery(key, board)
    board.drawBoard(cellsHit, numRun)
    return board


def batchRun(board, numScientists, numRuns):
    """
    Runs the simulation for each of numRuns years.
    During each run, each scientist in the department queries the board.
    At the end, an animation of the plots of each run is generated.
    """
    dept = [Scientist() for i in range(numScientists)]
    for j in range(numRuns):
        # keep track of which cells the scientists are hitting to check overlap
        if j % funding["replenishTime"] == 0:
            board.distributeFundingCell(chooseCellToFund, funding)

        board.cellsHit = {}
        for idx in range(len(dept)):
            scientist = dept[idx]
            scientist.funding -= funding["decrease"]
            location = scientist.chooseCell(board, weights)
            if location in board.cellsHit.keys():
                board.cellsHit[location].append(scientist)
            else:
                board.cellsHit.update({location : [scientist]})
            if (scientist.career == 0) or (scientist.funding <= funding["minimum"]):
                # when one scientist ends their career, another is introduced
                dept.remove(scientist)
                dept.append(Scientist())

        print("Board with payoff values: ", oneRun(board, board.cellsHit, j+1))
        print()

    currTotal = sum(board.flatten(board.getPayoffs()))
    print()
    print("Percentage of total payoff discovered: ", f"{((board.totalPayoff - currTotal)/board.totalPayoff)*100:.2f}")
    print()

    #animating plots
    frames = [Image.open(f'plots/plot{i+1}.png') for i in range(numRuns)]
    frame_one = frames[0]
    frame_one.save("animation.gif", format="GIF", append_images=frames,
            save_all=True, duration=500, loop=1)
    return

board = Board(5, 5, 0)
batchRun(board, numScientists=20, numRuns=20)