import numpy as np
import random
from classCell import *

class Scientist():
    def __init__(self):
        self.career = np.random.randint(1, 31)
        # citcount and impact corresponds to where you are in your career
        # they should be at least one so we don't divide by 0
        self.impact = abs(np.random.randint(20 - self.career, 35 - self.career)) + 1
        self.citcount = abs(np.random.randint(20 - self.career, 35 - self.career)) + 1

    def __repr__(self):
        """String representation of Scientist"""
        return str([self.impact, self.career, self.citcount])

    def getStarFactor(self):
        """calculates starFactor based on scientist's parameters"""
        overall = ((self.impact-(31 - self.career)) + (self.citcount-(31 - self.career)))/(31 - self.career) 
        return overall

    def probCell(self, board, weights):
        # Define the weights
        c = weights["citation"] * (1/self.citcount)
        i = weights["impact"] * (1/self.impact)
        e = weights["exploration"]


        # Calculate the probabilities for each cell
        probabilities = np.zeros_like(board.board)

        denominator = 0
        for x in range(board.rows):
            for y in range(board.cols):
                # i should be associated with board payoff value
                # e should be associated with numHits on the cell
                # c should be associated with num scientists on the cell
                denominator += np.exp((c * board.board[x][y].numSciHits) + (i * board.board[x][y].payoff) + (e * board.board[x][y].numHits))
        for j in range(board.rows):
            for k in range(board.cols):
                X1 = board.board[j][k]
                
                numerator = np.exp((c * X1.numSciHits) + (i * X1.payoff) + (e * X1.numHits))
                
                probabilities[j][k] = numerator / denominator

        return probabilities

    def chooseCell(self, board, weights):
        """chooses cell to query"""
        probs = self.probCell(board, weights)

        flatProbs = [item for sublist in probs for item in sublist]
        flatBoard = [board.board[i][j].location for j in range(board.cols) for i in range(board.rows)]
        choice = random.choices(flatBoard, weights=flatProbs, k=1)

        return choice[0]

    def sciQuery(self, location, board):
        """scientist queries chosen cell"""
        self.impact += board.board[location[0]][location[1]].cellQuery(board)
        self.career -= 1
        return self.impact

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
