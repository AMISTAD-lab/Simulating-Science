import seaborn as sn
import glob
from PIL import Image
from classCell import *
from classBoard import *
from classScientist import *

# def make_gif(frame_folder):
#     frames = [Image.open(image) for image in glob.glob(f"{frame_folder}/*.JPG")]
#     frame_one = frames[0]
#     frame_one.save("my_awesome.gif", format="GIF", append_images=frames,
#             save_all=True, duration=100, loop=0)
    
#     if __name__ == "__main__":
#         make_gif("/path/to/images")
#     return

def run(board, cellsHit, numRun):
    """runs query simulation for one year"""
    for key, val in cellsHit.items():
        if len(val) > 1:
            # randomly choose order in which scientists hit that same cell
            sciOrder = np.random.permutation(val)
            for scientist in sciOrder:
                scientist.sciQuery(key, board)
                scientist.cite(val)
                print("scientist: ", scientist)
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
        print("Board with payoff values: ", run(board, cellsHit, j+1))
        print()

    #animating plots
    frames = [Image.open(f'testplot{i+1}.png') for i in range(numRuns)]
    frame_one = frames[0]
    frame_one.save("animation.gif", format="GIF", append_images=frames,
            save_all=True, duration=500, loop=1)
    return

board = Board(5, 5)
batchRun(board, 10, 10)
