import numpy as np
#import classCell
#import classBoard
#import classDepartment
# from .classCell import *
# from .classBoard import Board
# from .classDepartment import Department

# from classBoard import *
# import classBoard as board
class Cell():
    def __init__(self, payoff, hidden=True, phase="e", numHits=0):
        # self.x = x
        # self.y = y
        self.payoff = payoff
    
    def __repr__(self):
        "string representation of Cell"
        return str(self.payoff)

    def query(self):
        self.numHits += 1
        if self.numHits > 4:
            self.phase = "i"
        elif self.numHits > 2:
            self.phase = "b"
        if self.phase == "e":
            self.payoff = self.payoff/10
        elif self.phase == "b":
            self.payoff = self.payoff/3
        else:
            self.payoff = self.payoff/10
        return self.payoff

class Board():
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.board = [[Cell(np.random.randint(low = 0, high = 20)) for i in range(self.rows)] for j in range(self.cols)]
        # self.numSci = Scientist()

    def __repr__(self):
        """string representation of Board"""
        return str(self.board)

class Department():
    def __init__(self, numScientists):
        self.numScientists = numScientists
    
    def __repr__(self):
        return str(self.makeScientists())

    def makeScientists(self):
        scientists = []
        for i in range(self.numScientists):
            # scientists have h-index and years left in career values
            scientists.append([np.random.randint(0, 50), np.random.randint(0, 30)])
        return scientists

dept = Department(5)
board = Board(5, 5)
    
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
