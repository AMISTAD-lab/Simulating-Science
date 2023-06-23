import numpy as np
import json
from PIL import Image
from classCell import *
from classBoard import *
from classScientist import *

# load in input parameters from json config file
with open("config.json", "r") as params:
    data = json.load(params)

weights = data["cellChoiceWeights"]
funding = data["fundingParams"]
chooseCellToFund = data["fundDistributionFactors"]
# semi-firm parameters that you could easily change but probabily won't need to
exp = data["expForProbabilities"]
N = data["payoffExtractionParams"]["N"]
D = data["payoffExtractionParams"]["D"]
p = data["payoffExtractionParams"]["p"]

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
            board.distributeFundingCell(chooseCellToFund, funding, exp)

        board.cellsHit = {}
        for idx in range(len(dept)):
            scientist = dept[idx]
            scientist.funding -= funding["decrease"]
            location = scientist.chooseCell(board, weights, exp)
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

board = Board(5, 5, 0, N, D, p)
batchRun(board, numScientists=20, numRuns=20)
