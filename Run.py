from classCell import *
from classBoard import *
from classScientist import *
from classDepartment import *

def run(board, cellsHit):
    """runs query simulation for one year"""
    for key, val in cellsHit.items():
        if len(val) > 1:
            # randomly choose order in which scientists hit that same cell
            sciOrder = np.random.permutation(val)
            print("sciOrder: ", sciOrder)
            for scientist in sciOrder:
                print("sciQuery: ", scientist.sciQuery(key, board))
        else:
            val[0].sciQuery(key, board)
    return board

def batchRun(board, numScientists, numRuns):
    """
    Runs the simulation for each of numRuns years.
    During each run, each scientist in the department queries the board.
    """
    dept = [Scientist() for i in range(numScientists)]

    for j in range(numRuns):
        # keep track of which cells the scientists are hitting to check overlap
        cellsHit = {}
        for scientist in dept:
            location = scientist.chooseCell(board)
            if location in cellsHit.keys():
                cellsHit[location].append(scientist)
            else:
                cellsHit.update({location : [scientist]})
            if scientist.career == 0:
                # when one scientist ends their career, another is introduced
                dept.remove(scientist)
                dept.append(Scientist())
        print(run(board, cellsHit))
        print()
    return

batchRun(Board(5, 5), 2, 3)

