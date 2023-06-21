from PIL import Image
import numpy as np
from classCell import *
from classBoard import *
from classScientist import *

weights = {
    "citation" : 0, 
    "impact" : 0.1,
    "exploration" : 1
}

funding = {
    "total" : 50,
    "decrease" : 1,
    "replenishTime" : 5,
    "minimum" : 10
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
                # print("scientist: ", scientist)
        else:
            val[0].sciQuery(key, board)
            # print("scientist: ", val[0])
    board.drawBoard(cellsHit, numRun)
    return board

def distributeFunding(dept):
    """
    distribute the funding allotted for each board
    """
    denominator = 0
    probabilities = np.zeros_like(dept)
    for sci in dept:
        star = sci.getStarFactor()
        # ensure numbers are in reasonable range
        if star <= -1:
            star = 1/abs(star)
        elif star >= 1:
            star = star
        else:
            star = 1

        denominator += np.exp(star)

    for i in range(len(dept)):
        star = dept[i].getStarFactor()
        if star <= -1:
            star = 1/abs(star)
        elif star >= 1:
            star = star
        else:
            star = 1

        numerator = np.exp(star)
        probabilities[i] = numerator / denominator
        # distribute funding based on starFactor for each scientist compared to whole department
        dept[i].funding += probabilities[i] * funding["total"]
        # dept[i].funding += funding["total"]/(len(dept))

    return [sci.funding for sci in dept]
    # go through scientists, add to their funding proportion of total

def batchRun(board, numScientists, numRuns):
    """
    Runs the simulation for each of numRuns years.
    During each run, each scientist in the department queries the board.
    At the end, an animation of the plots of each run is generated.
    """
    dept = [Scientist() for i in range(numScientists)]
    print("ogFunding: ", [sci.funding for sci in dept])
    for j in range(numRuns):
        # keep track of which cells the scientists are hitting to check overlap
        if j % funding["replenishTime"] == 0:
            print("funding: ", distributeFunding(dept))

        cellsHit = {}
        for idx in range(len(dept)):
            scientist = dept[idx]
            scientist.funding -= funding["decrease"]
            location = scientist.chooseCell(board, weights)
            if location in cellsHit.keys():
                cellsHit[location].append(scientist)
            else:
                cellsHit.update({location : [scientist]})
            if (scientist.career == 0) or (scientist.funding <= funding["minimum"]):
                # when one scientist ends their career, another is introduced
                dept.remove(scientist)
                dept.append(Scientist())
        # print statistics at the end of the run
        print()
        print("Board with payoff values: ", oneRun(board, cellsHit, j+1))
        print()
        # print("Department: ", dept)
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
batchRun(board, numScientists=10, numRuns=20)