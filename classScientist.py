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
        self.funding = abs(np.random.randint(20 - self.career, 35 - self.career)) + 1

    def __repr__(self):
        """String representation of Scientist"""
        return str([self.impact, self.career, self.citcount, self.funding])

    def getStarFactor(self):
        """calculates starFactor based on scientist's parameters"""
        num = (self.impact-(31 - self.career)) + (self.citcount-(31 - self.career)) + (self.funding-(31 - self.career))
        denom = (31 - self.career) 
        overall = num/denom
        return overall

    def probCell(self, board, weights, exp):
        """"generates a probability distribution over the cells"""
        # if they have a low citToCareer difference, then they value citations more
        # also, ensure numbers are in reasonable range
        citToCareer = (self.citcount-(31 - self.career))
        if citToCareer <= -1:
            c = weights["citation"] * abs(citToCareer)
        elif citToCareer >= 1:
            c = weights["citation"] * (1/citToCareer)
        else:
            c = weights["citation"]

        # if they have a low impactToCareer difference, then they value impact more
        impactToCareer = (self.impact-(31 - self.career))
        if impactToCareer <= -1:
            i = weights["impact"] * abs(impactToCareer)
        elif impactToCareer >= 1:
            i = weights["impact"] * (1/impactToCareer)
        else:
            i = weights["impact"]

        # if they have a low fundToCareer difference, then they value funding more
        fundToCareer = (self.funding-(31 - self.career))
        if fundToCareer <= -1:
            f = weights["funding"] * abs(fundToCareer)
        elif fundToCareer >= 1:
            f = weights["funding"] * (1/fundToCareer)
        else:
            f = weights["funding"]

        e = weights["exploration"]

        # Calculate the probabilities for each cell
        probabilities = np.zeros_like(board.board)
        denominator = 0
        for x in range(board.rows):
            for y in range(board.cols):
                cell = board.board[x][y]
                denominator += ((c * cell.numSciHits) + \
                    (i * board.getVisPayoff(cell.location)) + (f * cell.funds) + \
                    (e * 1/(1+cell.numHits))) ** exp
        for j in range(board.rows):
            for k in range(board.cols):
                cell = board.board[j][k]
                
                numerator = ((c * cell.numSciHits) + (i * board.getVisPayoff(cell.location)) + \
                    (e * 1/(1 + cell.numHits)) + (f * cell.funds)) ** exp
                
                probabilities[j][k] = numerator / denominator
        return probabilities

    def chooseCell(self, board, weights, exp):
        """chooses cell to query"""
        probs = self.probCell(board, weights, exp)
        flatBoard = [board.board[i][j].location for j in range(board.cols) for i in range(board.rows)]
        flatProbs = board.flatten(probs)
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
            star = sci.getStarFactor()
            # ensure numbers are in reasonable range
            if star <= -1:
                star = 1/abs(star)
            elif star >= 1:
                star = star
            else:
                star = 1

            denominator += np.exp(star) 

        for i in range(len(val)):
            star = val[i].getStarFactor()
            if star <= -1:
                star = 1/abs(star)
            elif star >= 1:
                star = star
            else:
                star = 1

            numerator = np.exp(star)
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