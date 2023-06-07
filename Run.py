import seaborn as sn
import glob
from PIL import Image
from classCell import *
from classBoard import *
from classScientist import *

weights = {
    "citation" : 0.1, 
    "impact" : 1,
    "exploration" : 0.1
}

def run(board, cellsHit, numRun, weights):
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

def batchRun(board, numScientists, numRuns):
    """
    Runs the simulation for each of numRuns years.
    During each run, each scientist in the department queries the board.
    At the end, an animation of the plots of each run is generated.
    """
    dept = [Scientist() for i in range(numScientists)]

    for j in range(numRuns):
        # keep track of which cells the scientists are hitting to check overlap
        cellsHit = {}
        for idx in range(len(dept)):
            scientist = dept[idx]
            location = scientist.chooseCell(board, weights)
            if location in cellsHit.keys():
                cellsHit[location].append(scientist)
            else:
                cellsHit.update({location : [scientist]})
            if scientist.career == 0:
                # when one scientist ends their career, another is introduced
                dept.remove(scientist)
                dept.append(Scientist())
        print("Board with payoff values: ", run(board, cellsHit, j+1, weights))
        print("dept: ", dept)
        print()

    #animating plots
    frames = [Image.open(f'plot{i+1}.png') for i in range(numRuns)]
    frame_one = frames[0]
    frame_one.save("animation.gif", format="GIF", append_images=frames,
            save_all=True, duration=500, loop=1)
    return

board = Board(5, 5)
batchRun(board, 20, 10)
