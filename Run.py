import numpy as np
import sqlite3
import copy
from PIL import Image
from classCell import *
from classBoard import *
from classScientist import *

# Defining database connection
conn = sqlite3.connect('data.db')

def oneRun(board, cellsHit, numRun, starFactorWeights, dept, exp, inputStr, numExperiment):
    """Runs query simulation for one year
    """
    # Retrives list of scientists querying each cell
    for cell, sciList in cellsHit.items():
        # If there is more than one scientist
        if len(sciList) > 1:
            # Randomly choose order in which scientists hit that same cell
            sciOrder = np.random.permutation(sciList)
            for scientist in sciOrder:
                scientist.sciQuery(cell, board)
                scientist.cite(sciList, starFactorWeights, exp) # Citing other scientists querying the same cell
                scientist.cellQueried = str(cell)
        # If there is only one scientist
        else:
            sciList[0].sciQuery(cell, board)
            sciList[0].cellQueried = str(cell)

    # Updates the cellsHit dictionary
    board.updateNumSciHits()

    # Updating database for current state of each cell
    for i in range(board.rows*board.cols):
        insert_query = "INSERT INTO cStats (inputStr, numExperiment, timeStep, location, totalFunds, totalPayoffExtracted, numQueries, uniqIds) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        flatBoard = board.flatten(board.board)
        cell = flatBoard[i].location

        # If a cell has been hit
        if flatBoard[i].location in cellsHit.keys():
            numQueries = len(cellsHit[cell]) # Retrieve number of queries for this cell
            # Update list of scientists querying the board by their unique IDs
            uniqIds = []
            for sci in cellsHit[cell]:
                uniqIds.append(sci.id)
            uniqIds = str(uniqIds)
        # If a cell has been hit, there are no queries and scientists
        else:
            numQueries = 0
            uniqIds = ""
        
        # Insert each cell's data into the database
        values = (inputStr, numExperiment, numRun, str(cell), cell.funds, float(board.getVisPayoff(cell)), numQueries, uniqIds)
        conn.execute(insert_query, values)
        conn.commit()

    # Updating database for current state of each scientist
    for i in range(len(dept)):
        insert_query = "INSERT INTO sStats (inputStr, numExperiment, timeStep, uniqId, totalFunds, starFactor, totalCitations, totalImpact, cellQueried) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        values = (inputStr, numExperiment, numRun, dept[i].id, dept[i].funding, dept[i].getStarFactor(starFactorWeights), dept[i].citcount, float(dept[i].impact), dept[i].cellQueried)
        conn.execute(insert_query, values)
        conn.commit()
    
    # Updating database for current state of the run
    insert_query = "INSERT INTO runStats (inputStrSci, numExpSci, timeStepSci, inputStrCell, numExpCell, timeStepCell, numCellsHit) VALUES (?, ?, ?, ?, ?, ?, ?)"
    values = (inputStr, numExperiment, numRun, inputStr, numExperiment, numRun, len(cellsHit))
    conn.execute(insert_query, values)
    conn.commit()

    # UNCOMMENT FOR VISUALIZATION
    # board.drawBoard(cellsHit, numRun, starFactorWeights)
    return board

def batchRun(board, numScientists, numRuns, data, input, numExperiment, currentScientist):
    """
    Runs the simulation for each of numRuns years.
    During each run, each scientist in the department queries the board.
    At the end, an animation of the plots of each run is generated.
    """
    # Firm parameters
    weights = data["scientistIncentives"]
    funding = data["fund"]
    chooseCellToFund = data["fundFactors"]
    
    # Semi-firm parameters
    exp = data["exp"]["num"]
    starFactorWeights = data["star"]
    totalScientists = numScientists
    totalDept = []

    # Defines a department (dept), a list of active scientists
    dept = [Scientist(i) for i in range(currentScientist, currentScientist + numScientists)]
    attrition = 0 # Scientists who left science
    for j in range(numRuns):
        oldDept = copy.copy(dept)
        totalDept = copy.copy(dept)
        # keep track of which cells the scientists are hitting to check overlap
        # Funding for the initial year is determined randomly
        board.distributeFundingCell(chooseCellToFund, funding, exp, starFactorWeights)

        # determines which scientists are at that location
        board.cellsHit = {}
        for idx in range(len(dept)):
            scientist = dept[idx]
            # update funding decrease for each scientist each year
            scientist.funding -= funding["decrease"]
            location = scientist.chooseCell(board, weights, exp)
            if location in board.cellsHit.keys():
                board.cellsHit[location].append(scientist)
            else:
                board.cellsHit.update({location : [scientist]})
            
            # scientists leaving science
            if (scientist.career == 0) or (scientist.funding <= funding["minimum"]):
                # attrition is the number of scientists who left science due to lack of funding
                if (scientist.funding <= funding["minimum"]):
                    attrition += 1
                # record the data of scientists who left science
                board.sStats.append([input, scientist.id, scientist.funding,
                    scientist.getStarFactor(starFactorWeights), scientist.citcount])
                
                #replace the old scientist's spot with a new scientist
                newScientist = Scientist(totalScientists+currentScientist)
                dept[idx] = newScientist
                totalDept.append(newScientist)
                totalScientists += 1
        oneRun(board, board.cellsHit, j+1, starFactorWeights, totalDept, exp, input, numExperiment)
        # print("Board with payoff values: ", oneRun(board, board.cellsHit, j+1, starFactorWeights, totalDept, exp, input))
        # print()

    currTotal = sum(board.flatten(board.getPayoffs()))
    print()
    print("Percentage of total payoff discovered: ", f"{((board.totalPayoff - currTotal)/board.totalPayoff)*100:.2f}")
    print()

    # # animating plots
    # frames = [Image.open(f'plots/plot{i+1}.png') for i in range(numRuns)]
    # frame_one = frames[0]
    # frame_one.save("animation.gif", format="GIF", append_images=frames,
    #         save_all=True, duration=500, loop=0)

    # add the scientist stats from the rest of the scientists at the very end
    for scientist in oldDept:
        board.sStats.append([input, scientist.id, scientist.funding,
            scientist.getStarFactor(starFactorWeights), scientist.citcount])

    # add percentage of board discovered and attrition stats
    board.bStats = [(board.totalPayoff - currTotal)/board.totalPayoff*100, 
                    attrition, attrition/totalScientists]

    # get cell funds and payoff of the board at the end
    for x in range(board.rows):
            for y in range(board.cols):
                cell = board.board[x][y]
                board.cStats.append([input, cell.location, cell.totalFunds, 
                                    board.getVisPayoff(cell.location), board.getRemainingPayoff(cell.location), board.getTotalPayoff(cell.location)])

    return (currentScientist+totalScientists), [board.bStats, board.cStats, board.sStats]