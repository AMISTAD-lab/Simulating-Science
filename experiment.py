import json
import csv
import sqlite3
import latextable
import pandas as pd
import os
from tabulate import tabulate
from texttable import Texttable
from Run import *

inp = "default.json"
with open(inp, "r") as params:
    data = json.load(params)

# setting up sql database connection
conn = sqlite3.connect('data.db')

# Define the schema

conn.execute('''CREATE TABLE IF NOT EXISTS bStats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    inputStr STRING,
                    payoffExtracted FLOAT,
                    attrition INTEGER,
                    attritionRate FLOAT
                )''')

conn.execute('''CREATE TABLE IF NOT EXISTS cStats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    inputStr STRING,
                    numRun INTEGER,
                    location STRING,
                    funds FLOAT,
                    payoffExtracted FLOAT
                )''')

conn.execute('''CREATE TABLE IF NOT EXISTS sStats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    inputStr STRING,
                    numRun INTEGER,
                    uniqId INTEGER,
                    funds FLOAT,
                    starFactor FLOAT,
                    citations INTEGER
                )''')

conn.execute('''CREATE TABLE IF NOT EXISTS runStats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    inputStrSci STRING,
                    numRunSci INTEGER,
                    inputStrCell STRING,
                    numRunCell INTEGER,
                    FOREIGN KEY (inputStrSci) REFERENCES sStats(inputStr),
                    FOREIGN KEY (numRunSci) REFERENCES sStats(numRun),
                    FOREIGN KEY (inputStrCell) REFERENCES cStats(inputStr),
                    FOREIGN KEY (numRunCell) REFERENCES cStats(numRun)
                )''')
conn.commit()

def writeBStats(inputStr, bStats):
    insert_query = "INSERT INTO bStats (inputStr, payoffExtracted, attrition, attritionRate) VALUES (?, ?, ?, ?)"
    values = (inputStr, bStats[0], bStats[1], bStats[2])
    conn.execute(insert_query, values)
    conn.commit()

def experiment(numScientists, numRuns, numExperiments, boardDimension):
    """
    runs with given parameters and saves to csv file
    enter the input(s) in the default.json you want to vary from the default in the command line like so:
        [paramType] [param] [newValue]
        cellChoiceWeights citation 1
        fundDistributionFactors numHits 0.5
    """
    inputStr = input()
    fullInput = []
    while inputStr != "":
        if len(inputStr.split()) == 3:
            typeParam = inputStr.split()[0]
            param = inputStr.split()[1]
            newNum = float(inputStr.split()[2])
            if typeParam in data.keys() and param in data[typeParam].keys():
                data[typeParam][param] = newNum
                fullInput.append(inputStr)
            else:
                print("parameter you entered does not follow the default style", typeParam, param)
                return
        else:
            print("check input format - input must be of different length")
            return
        inputStr = input()
    fullInput = ", ".join(fullInput)

    N = data["payoffExtraction"]["N"]
    D = data["payoffExtraction"]["D"]
    p = data["payoffExtraction"]["p"]
    probZero = data["zeroPayoff"]["probability"]

    bStats = []
    cStats = []
    sStats = []
    for x in range(numExperiments):
        board = Board(boardDimension, boardDimension, probZero, N, D, p)
        batchResult = batchRun(board, numScientists, numRuns, data, fullInput)
        bStats.append(batchResult[0])
        cStats.append(batchResult[1])
        sStats.append(batchResult[2])
        writeBStats(fullInput, bStats[x])

    # write stats to csv output file
    # each experiment's stats appear in one row
    boardStats = "boardStats.csv"
    with open(boardStats, 'w', newline='') as file:
        writer = csv.writer(file)
        header = ['Percentage Payoff Discovered', 'Attrition', 'Attrition Rate']
        writer.writerow(header)
        writer.writerows(bStats)

    cellStats = "cellStats.csv"
    with open(cellStats, 'w', newline='') as file:
        writer = csv.writer(file)
        header = ['Input', 'Location', 'Funds', 'Payoff Extracted']
        writer.writerow(header)
        for l in cStats:
            writer.writerows(l)
 
    sciStats = "sciStats.csv"
    with open(sciStats, 'w', newline='') as file:
        writer = csv.writer(file)
        header = ['Input', 'ID', 'Total Funding Accumulated', 'starFactor', 'Citation Count']
        writer.writerow(header)
        for l in sStats:
            writer.writerows(l)

    conn.close()
    return
    
def generateLaTeX(listOfFolders):
    """
    Outputs LaTeX code to generate tables with simulation statistics.
    Takes in a list of csv file names within folders in the repository.
    """
    payoffs = []
    attrRate = []
    inputStr = []
    cellPayoff = []
    cellFund = []
    boardRows = [['Input', 'Average Percentage of Payoff Discovered', 'Average Attrition Rate']]
    cellRows = [['Input', 'Average Difference between Funding and Payoff Extracted']]
    sciRows = [['Input', 'Average Difference between Funding and Citation Count']]
    for folder in listOfFolders:
        dirList = os.listdir(folder)
        for file in dirList:
            with open(str(folder) + "/" + str(file)) as file_obj:
                data = pd.read_csv(str(folder) + "/" + str(file))
                if file == 'cellStats.csv':
                    inputStr = data['Input'].tolist()
                    cellPayoff = data['Payoff Extracted'].tolist() 
                    cellFund = data['Funds'].tolist()
                elif file == 'boardStats.csv':
                    payoffs = data['Percentage Payoff Discovered'].tolist()
                    attrRate = data['Attrition Rate'].tolist()
                elif file == 'sciStats.csv':
                    sciFund = data['Total Funding Accumulated'].tolist()
                    sciCitCount = data['Citation Count'].tolist()
        citCountToFund = [abs(sciFund[i] - sciCitCount[i]) for i in range(len(sciFund))]
        avgCitCountToFund = sum(citCountToFund) / len(citCountToFund)
        CIavgCitCountToFund = avgCitCountToFund - (avgCitCountToFund - 1.96*math.sqrt(np.var(citCountToFund)/len(citCountToFund)))

        payoffToFund = [abs(cellPayoff[i] - cellFund[i]) for i in range(len(cellPayoff))]
        avgPayoffToFund = sum(payoffToFund) / len(payoffToFund)
        CIavgPayoffToFund = avgPayoffToFund - (avgPayoffToFund - 1.96*math.sqrt(np.var(payoffToFund)/len(payoffToFund)))

        avgPayoff = sum(payoffs) / len(payoffs)
        CIPayoff = avgPayoff - (avgPayoff - 1.96*math.sqrt(np.var(payoffs)/len(payoffs)))

        avgAttrRate = sum(attrRate) / len(attrRate)
        CIAttrRate = avgAttrRate - (avgAttrRate - 1.96*math.sqrt(np.var(attrRate)/len(attrRate)))
        if type(inputStr[0]) == str:
            boardRows.append([inputStr[0],
                str(f'{avgPayoff:0.3f}') + " $\pm$ " + str(f'{CIPayoff:0.3f}'),
                str(f'{avgAttrRate:0.3f}') + " $\pm$ " + str(f'{CIAttrRate:0.3f}')])
            cellRows.append([inputStr[0],
                str(f'{avgPayoffToFund:0.3f}') + " $\pm$ " + str(f'{CIavgPayoffToFund:0.3f}')])
            sciRows.append([inputStr[0],
                str(f'{avgCitCountToFund:0.3f}') + " $\pm$ " + str(f'{CIavgCitCountToFund:0.3f}')])
        else:
            boardRows.append(["Default",
                str(f'{avgPayoff:0.3f}') + " $\pm$ " + str(f'{CIPayoff:0.3f}'),
                str(f'{avgAttrRate:0.3f}') + " $\pm$ " + str(f'{CIAttrRate:0.3f}')])
            cellRows.append(["Default",
                str(f'{avgPayoffToFund:0.3f}') + " $\pm$ " + str(f'{CIavgPayoffToFund:0.3f}')])
            sciRows.append(["Default",
                str(f'{avgCitCountToFund:0.3f}') + " $\pm$ " + str(f'{CIavgCitCountToFund:0.3f}')])

    # Code inspired by https://colab.research.google.com/drive/1Iq10lHznMngg1-Uoo-QtpTPii1JDYSQA?usp=sharing#scrollTo=K7NNR1Vg40Vo
    table = Texttable()
    table.set_cols_align(["c"] * 3)
    table.set_deco(Texttable.HEADER | Texttable.VLINES)
    table.add_rows(boardRows)

    tabulate(boardRows, headers='firstrow', tablefmt='latex')
    print(latextable.draw_latex(table))

    table = Texttable()
    table.set_cols_align(["c"] * 2)
    table.set_deco(Texttable.HEADER | Texttable.VLINES)
    table.add_rows(cellRows)

    tabulate(cellRows, headers='firstrow', tablefmt='latex')
    print(latextable.draw_latex(table))

    table = Texttable()
    table.set_cols_align(["c"] * 2)
    table.set_deco(Texttable.HEADER | Texttable.VLINES)
    table.add_rows(sciRows)

    tabulate(sciRows, headers='firstrow', tablefmt='latex')
    print(latextable.draw_latex(table))

    return

def generateBar(listOfFolders):
    bars1 = []
    yer1 = []
    for folder in listOfFolders:
        dirList = os.listdir(folder)
        for file in dirList:
            with open(file) as file_obj:
                data = pd.read_csv(file)
                if file == 'boardStats.csv':
                    payoffs = data['Percentage Payoff Discovered'].tolist()
            
            avgPayoff = sum(payoffs) / len(payoffs)
            bars1 += [avgPayoff]
            CIPayoff = avgPayoff - (avgPayoff - 1.96*math.sqrt(np.var(payoffs)/len(payoffs)))
            yer1 += [CIPayoff]

        # width of the bars
        barWidth = 0.3
        # The x position of bars
        r1 = np.arange(len(bars1))
        r2 = [x + barWidth for x in r1]

        # Create blue bars
        plt.bar(r1, bars1, width = barWidth, color = 'blue', edgecolor = 'black', yerr=yer1, capsize=7, label='poacee')

        # general layout
        plt.xticks([r + barWidth for r in range(len(bars1))], ['cond_A', 'cond_B', 'cond_C'])
        plt.ylabel('height')
        plt.legend()

        # Show graphic
        plt.show()
        return