import numpy as np
import sqlite3
from PIL import Image
from classCell import *
from classBoard import *
from classScientist import *

# setting up sql database connection
conn = sqlite3.connect('data.db')

def oneRun(board, cellsHit, numRun, starFactorWeights, dept, numScientists, numRuns):
    """runs query simulation for one year"""
    for key, val in cellsHit.items():
        #more than one scientist
        if len(val) > 1:
            # randomly choose order in which scientists hit that same cell
            sciOrder = np.random.permutation(val)
            for scientist in sciOrder:
                scientist.sciQuery(key, board)
                scientist.cite(val, starFactorWeights)
        else:
            val[0].sciQuery(key, board)
    board.updateNumSciHits()
    for i in range(len(dept)):
        insert_query = '''INSERT INTO sStats (uniqId''' + str(i) + ''', funds''' + str(i) + ''', starFactor''' + str(i) + ''', citations''' + str(i) + ''') VALUES (?, ?, ?, ?)'''
        values = (dept[i].id, dept[i].funding, dept[i].getStarFactor(starFactorWeights), dept[i].citcount)
        conn.execute(insert_query, values)
        conn.commit()

        conn.execute('''UPDATE sStats SET uniqId''' + str(i) + ''' = ? WHERE id = ?''', (dept[i].id, numRun))
        conn.execute('''UPDATE sStats SET funds''' + str(i) + ''' = ? WHERE id = ?''', (dept[i].funding, numRun))
        conn.execute('''UPDATE sStats SET starFactor''' + str(i) + ''' = ? WHERE id = ?''', (dept[i].getStarFactor(starFactorWeights), numRun))
        conn.execute('''UPDATE sStats SET citations''' + str(i) + ''' = ? WHERE id = ?''', (dept[i].citcount, numRun))

        conn.execute('''DELETE from sStats where id > ''' + str(numRuns))
        conn.commit()

    for i in range(board.rows*board.cols):
        insert_query = '''INSERT INTO cStats (location''' + str(i) + ''', funds''' + str(i) + ''', payoffExtracted''' + str(i) + ''') VALUES (?, ?, ?)'''
        l = board.flatten(board.board)
        values = (str(l[i].location), l[i].funds, board.getVisPayoff(l[i].location))
        conn.execute(insert_query, values)
        conn.commit()

        l = board.flatten(board.board)
        conn.execute('''UPDATE cStats SET location''' + str(i) + ''' = ? WHERE id = ?''', (str(l[i].location), numRun))
        conn.execute('''UPDATE cStats SET funds''' + str(i) + ''' = ? WHERE id = ?''', (l[i].funds, numRun))
        conn.execute('''UPDATE cStats SET payoffExtracted''' + str(i) + ''' = ? WHERE id = ?''', (board.getVisPayoff(l[i].location), numRun))

        conn.execute('''DELETE from cStats where id > ''' + str(numRuns))
        conn.commit()

    conn.commit()
    # UNCOMMENT FOR VISUALIZATION
    #board.drawBoard(cellsHit, numRun, starFactorWeights)
    return board

def batchRun(board, numScientists, numRuns, data):
    """
    Runs the simulation for each of numRuns years.
    During each run, each scientist in the department queries the board.
    At the end, an animation of the plots of each run is generated.
    """
    weights = data["scientistIncentives"]
    funding = data["fund"]
    chooseCellToFund = data["fundFactors"]
    # semi-firm parameters that you could easily change but probabily won't need to
    exp = data["exp"]["num"]
    starFactorWeights = data["star"]
    totalScientists = numScientists

    dept = [Scientist(i) for i in range(numScientists)]
    attrition = 0

    # Define the table structure for cells and scientists
    conn.execute('''DROP TABLE IF EXISTS cStats''')

    conn.execute('''CREATE TABLE IF NOT EXISTS cStats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT
                    )''')

    for i in range(board.rows*board.cols):
        conn.execute('''ALTER TABLE cStats ADD location''' + str(i) + ''' STRING''')
        conn.execute('''ALTER TABLE cStats ADD funds''' + str(i) + ''' FLOAT''')
        conn.execute('''ALTER TABLE cStats ADD payoffExtracted''' + str(i) + ''' FLOAT''')
    
    conn.execute('''DROP TABLE IF EXISTS sStats''')
    conn.execute('''CREATE TABLE IF NOT EXISTS sStats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT
                    )''')

    for i in range(numScientists):
        conn.execute('''ALTER TABLE sStats ADD uniqId''' + str(i) + ''' INTEGER''')
        conn.execute('''ALTER TABLE sStats ADD funds''' + str(i) + ''' FLOAT''')
        conn.execute('''ALTER TABLE sStats ADD starFactor''' + str(i) + ''' FLOAT''')
        conn.execute('''ALTER TABLE sStats ADD citations''' + str(i) + ''' INTEGER''')


    conn.commit()

    for j in range(numRuns):
        # keep track of which cells the scientists are hitting to check overlap
        # funding for the first year is determined randomly
        board.distributeFundingCell(chooseCellToFund, funding, exp, starFactorWeights)

        # gives which scientists are at that location
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
            # when one scientist ends their career, another is introduced
            if (scientist.career == 0) or (scientist.funding <= funding["minimum"]):
                # attrition is the number of scientists who left science due to lack of funding
                if (scientist.funding <= funding["minimum"]):
                    attrition += 1
                # record the data of scientists who left science
                board.sStats.append(scientist.id)
                board.sStats.append(scientist.funding)
                board.sStats.append(scientist.getStarFactor(starFactorWeights))
                board.sStats.append(scientist.citcount)
                dept.remove(scientist)
                dept.append(Scientist(totalScientists))
                totalScientists += 1
        oneRun(board, board.cellsHit, j+1, starFactorWeights, dept, numScientists, numRuns)
        # print("Board with payoff values: ", oneRun(board, board.cellsHit, j+1, starFactorWeights, dept, numScientists, numRuns))
        # print()

    currTotal = sum(board.flatten(board.getPayoffs()))
    print()
    print("Percentage of total payoff discovered: ", f"{((board.totalPayoff - currTotal)/board.totalPayoff)*100:.2f}")
    print()

    # #animating plots
    # frames = [Image.open(f'plots/plot{i+1}.png') for i in range(numRuns)]
    # frame_one = frames[0]
    # frame_one.save("animation.gif", format="GIF", append_images=frames,
    #         save_all=True, duration=500, loop=0)

    # add the scientist stats from the rest of the scientists at the very end
    for scientist in dept:
        board.sStats.append(scientist.id)
        board.sStats.append(scientist.funding)
        board.sStats.append(scientist.getStarFactor(starFactorWeights))
        board.sStats.append(scientist.citcount)

    # add percentage of board discovered and attrition stats
    board.bStats = [(board.totalPayoff - currTotal)/board.totalPayoff*100, 
                    attrition, attrition/totalScientists]

    # get cell funds and payoff of the board at the end
    for x in range(board.rows):
            for y in range(board.cols):
                cell = board.board[x][y]
                board.cStats.append(cell.location)
                board.cStats.append(cell.totalFunds)
                board.cStats.append(board.getVisPayoff(cell.location))
    

    return [board.bStats, board.cStats, board.sStats]

