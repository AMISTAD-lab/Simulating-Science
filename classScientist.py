import numpy as np
import random
from classCell import *

class Scientist():
    def __init__(self):
        self.career = np.random.randint(1, 31)
        # citcount and impact corresponds to where you are in your career
        self.impact = abs(np.random.randint(20 - self.career, 35 - self.career))
        self.citcount = abs(np.random.randint(20 - self.career, 35 - self.career))

    def __repr__(self):
        """String representation of Scientist"""
        return str([self.impact, self.career, self.citcount])

    def getStarFactor(self):
        """calculates starFactor based on scientist's parameters"""
        overall = ((self.impact-(31 - self.career)) + (self.citcount-(31 - self.career)))/(31 - self.career) 
        return overall
    
    def probCell(self, weights, board):
        # Define the weights
        c = weights["citation"]
        i = weights["impact"]
        e = weights["exploration"]


        # Calculate the probabilities for each cell
        probabilities = np.zeros_like(board)

        denominator = 0
        for x in range(board.rows):
            for y in range(board.cols):
                denominator += np.exp((c * self.citcount) + (i * self.impact) + (e * board[x, y]))
        for j in range(board.rows):
            for k in range(board.cols):
                X1 = board[j, k]
                
                numerator = np.exp((c * self.citcount) + (i * self.impact) + (e * X1))
                
                probabilities[j, k] = numerator / denominator

        return probabilities

    def citeProbs(self, val):
        """probability distribution of citing scientists in a cell"""
        # Calculate the probabilities for each cell
        probabilities = np.zeros_like(val)

        denominator = 0
        for sci in val:
            denominator += np.exp(sci.getStarFactor()) 
        for i in range(len(val)):
            numerator = np.exp(val[i].getStarFactor())
            probabilities[i] = numerator / denominator

        return probabilities

    def cite(self, val):
        """decides which other scientists in the cell get cited"""
        probs = self.citeProbs(val)

        # if choosing 1 scientist to cite
        # choice = random.choices(val, weights=probs, k=1)
        # if choice != self:
        #     choice.citcount += 1

        # if choosing multiple people to cite
        for i in range(len(val)):
            if probs[i] > (1/len(val)):
                # taking out self citing
                if val[i] != self:
                    val[i].citcount += 1
        return

    def probHerd(self):
        """generate the probability of the scientist following the herd 
        based on h index and career"""
        pHerd = abs((self.impact-(31 - self.career))/(31 - self.career))
        if (self.impact > (31 - self.career)):
            if pHerd > 1:
                pHerd = 0
            else:
                pHerd = 1 - pHerd
        else:
            if pHerd > 1:
                pHerd = 1
        return pHerd

    def chooseCell(self, board, weights):
        """decides which cell the scientist will query according to payoff"""
        # dictionary of discovered cells' locations and payoff values
        discoveredPayoffs = {}
        maxPayoff = 0.0

        for x in board.discovered:
            discoveredPayoffs.update({board.board[x[0]][x[1]].payoff : board.board[x[0]][x[1]]})

        choice = np.random.binomial(1, self.probHerd())
        # choice = 1 --> they follow the herd
        if (choice == 1 and len(list(discoveredPayoffs.keys())) > 0) or (choice == 0 and len(board.undiscovered) == 0):
                maxPayoff = max(list(discoveredPayoffs.keys()))
                location = discoveredPayoffs.get(maxPayoff).location
        # choice = 0 --> choose randomly from undiscovered cells
        else:
            location = random.choice(board.undiscovered)

        return location

    def sciQuery(self, location, board):
        """scientist queries chosen cell"""
        self.impact += board.board[location[0]][location[1]].cellQuery(board)
        self.career -= 1
        return self.impact
