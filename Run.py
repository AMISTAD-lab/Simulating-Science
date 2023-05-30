from classCell import *
from classBoard import *
from classScientist import *
from classDepartment import *

board = Board(2, 2)
print(board)

dept = []
numScientists = 1
for i in range(numScientists):
    dept.append(Scientist())
for scientist in dept:
    while scientist.career != 0:
        # do a query while career is not over
        print("SCIQUERY: ", scientist.sciQuery(board))
        print("board: ", board)
        print("dept: ", dept)
        print()
        scientist.career -= 1
print("undiscovered: ", board.undiscovered)
print("discovered: ", board.discovered)
# print(board.randomRange)
