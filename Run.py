from PIL import Image
import numpy as np
from classCell import *
from classBoard import *
from classScientist import *

weights = {
    "citation" : 0.5, 
    "impact" : 0.5,
    "exploration" : 0.5,
    "funding" : 0.5
}

funding = {
    "total" : 100,
    "decrease" : 1,
    "replenishTime" : 5,
    "minimum" : 10
}

chooseCellToFund = {
    "visPayoff" : 0.5,
    "starFactor" : 0.5,
    "numHits" : 0.5,
    "numSciHits" : 0.5
}

def oneRun(board, cellsHit, numRun):
    """runs query simulation for one year"""
    for key, val in cellsHit.items():
        if len(val) > 1:
            # randomly choose order in which scientists hit that same cell
            sciOrder = np.random.permutation(val)
            for scientist in sciOrder:
                scientist.sciQuery(key, board)
                scientist.cite(val)
        else:
            val[0].sciQuery(key, board)
    board.drawBoard(cellsHit, numRun)
    return board

def distributeFundingSci(dept, cellFunding):
    """
    distribute the funding allotted for each cell to the scientists in the cell
    """
    denominator = 0
    probabilities = np.zeros_like(dept)
    for sci in dept:
        star = sci.getStarFactor()
        # print("star: ", star)
        # ensure numbers are in reasonable range
        if star <= -1:
            star = 1/abs(star)
        elif star >= 1:
            star = star
        else:
            star = 1
        denominator += np.exp(star)

    for i in range(len(dept)):
        star = dept[i].getStarFactor()
        if star <= -1:
            star = 1/abs(star)
        elif star >= 1:
            star = star
        else:
            star = 1
        numerator = np.exp(star)
        
        probabilities[i] = numerator / denominator
        # distribute funding based on starFactor for each scientist compared to whole department
        dept[i].funding += probabilities[i] * cellFunding
        # to debug code, you might want to run the following line to distribute funding evenly
        # dept[i].funding += funding["total"]/(len(dept))

    return [sci.funding for sci in dept]
    # go through scientists, add to their funding proportion of total

def distributeFundingCell(board):
    """distributes funding to each cell based on historical numHits"""
    # Calculate the probabilities for each cell
    probabilities = np.zeros_like(board.board)
    denominator = 0
    for x in range(board.rows):
        for y in range(board.cols):
            cell = board.board[x][y]
            #find the average of scientists' starFactors in this cell
            starSum = 0
            avgStarSum = 0
            if cell.location in board.cellsHit.keys():
                for sci in board.cellsHit[cell.location]:
                    starSum += sci.getStarFactor()
                avgStarSum = starSum/cell.numSciHits

            # account for the fact that starFactor can be negative
            if avgStarSum <= -1:
                starWeight = chooseCellToFund["starFactor"] * 1/abs(avgStarSum)
            elif avgStarSum >= 1:
                starWeight = chooseCellToFund["starFactor"] * (avgStarSum)
            else:
                starWeight = chooseCellToFund["starFactor"]
            #calculates the rest of the weights
            visWeight = chooseCellToFund["visPayoff"] * (board.getVisPayoff(cell.location))
            numHitsWeight = chooseCellToFund["numHits"] * (cell.numHits)
            recentHitsWeight = chooseCellToFund["numSciHits"] * (cell.numSciHits)
            # print("fundingWeights: ", starWeight, visWeight, numHitsWeight, recentHitsWeight)

            #Note: magic number 3 
            denominator += (visWeight + starWeight + numHitsWeight + recentHitsWeight)**3
    
    for j in range(board.rows):
        for k in range(board.cols):
            cell = board.board[j][k]
            #find the average of scientists' starFactors in this cell
            starSum = 0
            avgStarSum = 0
            if cell.location in board.cellsHit.keys():
                for sci in board.cellsHit[cell.location]:
                    starSum += sci.getStarFactor()
                avgStarSum = starSum/cell.numSciHits

            # account for the fact that starFactor can be negative
            if avgStarSum <= -1:
                starWeight = chooseCellToFund["starFactor"] * 1/abs(avgStarSum)
            elif avgStarSum >= 1:
                starWeight = chooseCellToFund["starFactor"] * (avgStarSum)
            else:
                starWeight = chooseCellToFund["starFactor"]

            visWeight = chooseCellToFund["visPayoff"] * (board.getVisPayoff(cell.location))
            numHitsWeight = chooseCellToFund["numHits"] * (cell.numHits)
            recentHitsWeight = chooseCellToFund["numSciHits"] * (cell.numSciHits)

            numerator = (visWeight + starWeight + numHitsWeight + recentHitsWeight)**3
            probabilities[j][k] = numerator / denominator

            #fund cell and then scientist based on probabilities
            cell.funds = probabilities[j][k] * funding["total"]
            if cell.location in board.cellsHit.keys():
                distributeFundingSci(board.cellsHit[cell.location], cell.funds)
    return probabilities

def batchRun(board, numScientists, numRuns):
    """
    Runs the simulation for each of numRuns years.
    During each run, each scientist in the department queries the board.
    At the end, an animation of the plots of each run is generated.
    """
    dept = [Scientist() for i in range(numScientists)]
    print("ogFunding: ", [sci.funding for sci in dept])
    for j in range(numRuns):
        # keep track of which cells the scientists are hitting to check overlap
        if j % funding["replenishTime"] == 0:
            # print("cellsHit: ", board.cellsHit)
            distributeFundingCell(board)
            # print("funding: ", distributeFundingCell(board))

        board.cellsHit = {}
        for idx in range(len(dept)):
            scientist = dept[idx]
            scientist.funding -= funding["decrease"]
            location = scientist.chooseCell(board, weights)
            if location in board.cellsHit.keys():
                board.cellsHit[location].append(scientist)
            else:
                board.cellsHit.update({location : [scientist]})
            if (scientist.career == 0) or (scientist.funding <= funding["minimum"]):
                # when one scientist ends their career, another is introduced
                dept.remove(scientist)
                dept.append(Scientist())
        # print statistics at the end of the run
        # print()
        oneRun(board, board.cellsHit, j+1)
        # print("Board with payoff values: ", oneRun(board, board.cellsHit, j+1))
        # print()
        # print("Department: ", dept)
    currTotal = sum(board.flatten(board.getPayoffs()))
    print()
    print("Percentage of total payoff discovered: ", f"{((board.totalPayoff - currTotal)/board.totalPayoff)*100:.2f}")
    print()

    #animating plots
    frames = [Image.open(f'plots/plot{i+1}.png') for i in range(numRuns)]
    frame_one = frames[0]
    frame_one.save("animation.gif", format="GIF", append_images=frames,
            save_all=True, duration=500, loop=1)
    return

board = Board(5, 5, 0)
batchRun(board, numScientists=20, numRuns=20)