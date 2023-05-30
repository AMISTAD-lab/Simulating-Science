from classCell import *
from classBoard import *
from classScientist import *
from classDepartment import *

#dept = Department(5)
board = Board(2, 2)
print(board)

dept = []
numScientists = 1
for i in range(numScientists):
    dept.append(Scientist())
for scientist in dept:
    print(scientist)
    while scientist.career != 0:
        # do a query while career is not over
        # scientist.sciQuery(board)
        print("SCIQUERY: ")
        print(scientist.sciQuery(board))
        print(board)
        print(dept)
        scientist.career -= 1
print("undiscovered: ", board.undiscovered)
print("discovered: ", board.discovered)
# while scientist has career
# query board based on hindex and career state --> influences herd mentality
# ultimately decides to either randomly explore space or 
# different space (not hidden one) depending on highest payoff
# scientists then visit cells and take some of their payoff which affects hindex
# (career also decreases by a time step)
# on the board side, cells become unhidden when enough alterations
# lead to breakthrough/incremental phase
