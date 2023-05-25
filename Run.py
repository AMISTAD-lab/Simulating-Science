from classCell import *
from classBoard import *
from classDepartment import *

dept = Department(5)
board = Board(5, 5)
print(dept)
print(board) 
for scientist in dept.makeScientists():
    while scientist[1] != 0:
        # do a query while career is not over
        scientist[1] -= 1
# while scientist has career
# query board based on hindex and career state --> influences herd mentality
# ultimately decides to either randomly explore space or 
# different space (not hidden one) depending on highest payoff
# scientists then visit cells and take some of their payoff which affects hindex
# (career also decreases by a time step)
# on the board side, cells become unhidden when enough alterations
# lead to breakthrough/incremental phase
