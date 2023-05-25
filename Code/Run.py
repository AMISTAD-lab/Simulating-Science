import numpy as np
from classBoard import *
import classBoard as board

#class Cell:
#     def __init__(self, payoff, hidden=True):
#         # self.x = x
        # self.y = y
        self.payoff = payoff
    
    def __repr__(self):
        "string representation of Cell"
        return str(self.payoff)

class Board():
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.board = [[Cell(np.random.randint(low = 0, high = 20)) for i in range(self.rows)] for j in range(self.cols)]

    def __repr__(self):
        """string representation of Board"""
        return str(self.board)



print(Board(5, 5))

# #generate the array with different valued payoffs
# arr = np.random.randint(low = 0, high = 20, size = (5, 5))

# # create scientist vectors with the parameters:
# # h-index, career stage (based on number of queries/time steps)
# # each query = 1 year of career stage
# numScientists = 5
# scientists = []
# for i in range(numScientists):
#     scientists.append([np.random.randint(0, 50), np.random.randint(0, 30)])
# for scientist in scientists:
#     # note hIndex = scientist[0]
#     # note career = scientist[1]
#     while scientist[1] != 0:
#         scientist[1] -= 1
        
# print(scientists)
# print(arr)
# print(Board(5, 5))