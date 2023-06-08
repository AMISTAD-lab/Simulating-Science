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
        """"generates a probability distribution over the cells"""
        citToCareer = (self.citcount-(31 - self.career))
        # if they have a low citToCareer difference, then they value citations more
        if citToCareer < 0:
            c = weights["citation"] * abs(citToCareer)
        elif citToCareer == 0:
            c = weights["citation"]
        # if they have a high citToCareer difference, then they value citations less
        else:
            c = weights["citation"] * (1/citToCareer)

        impactToCareer = (self.impact-(31 - self.career))
        # if they have a low impactToCareer difference, then they value impact more
        if impactToCareer < 0:
            i = weights["impact"] * abs(impactToCareer)
        elif impactToCareer == 0:
            i = weights["impact"]
        # if they have a high impactToCareer difference, then they value impact less
        else:
            i = weights["impact"] * (1/impactToCareer)

        e = weights["exploration"]
        print("cie: ", c, i, e)

        # Calculate the probabilities for each cell
        probabilities = np.zeros_like(board.board)
        denominator = 0
        for x in range(board.rows):
            for y in range(board.cols):
                # i should be associated with board payoff value
                # e should be associated with numHits on the cell
                # c should be associated with num scientists on the cell
                # scientists see how much payoff has been extracted (visiblePayoff)
                visiblePayoff = (board.originalPays[y][x] - board.board[x][y].payoff)
                denominator += np.exp((c * board.board[x][y].numSciHits) + (i * visiblePayoff) + (e * 1/(1+board.board[x][y].numHits)))
        for j in range(board.rows):
            for k in range(board.cols):
                X1 = board.board[j][k]
                visiblePayoff = (board.originalPays[k][j] - board.board[j][k].payoff)
                
                numerator = np.exp((c * X1.numSciHits) + (i * visiblePayoff) + (e * 1/(1 + X1.numHits)))
                
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

        # randomly choose how many other scientists to cite, not including themselves
        numCites = np.random.randint(0, len(val) + 1)
        
        choice = random.choices(val, weights=probs, k=numCites)
        for elem in choice:
            if elem != self:
                elem.citcount += 1
        return
