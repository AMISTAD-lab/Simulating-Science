import json
import csv
from Run import *

inp = "default.json"
with open(inp, "r") as params:
    data = json.load(params)

def experiment(numScientists, numRuns, numExperiments):
    """
    runs with given parameters and saves to csv file
    enter the input(s) in the default.json you want to vary from the default in the command line like so:
        [paramType] [param] [newValue]
        cellChoiceWeights citation 1
        fundDistributionFactors numHits 0.5
    """
    inputStr = input()
    while inputStr != "":
        if len(inputStr.split()) == 3:
            typeParam = inputStr.split()[0]
            param = inputStr.split()[1]
            newNum = float(inputStr.split()[2])
            if typeParam in data.keys() and param in data[typeParam].keys():
                data[typeParam][param] = newNum
            else:
                print("parameter you entered does not follow the default style", typeParam, param)
                return
        else:
            print("check input format - input must be of different length")
            return
        inputStr = input()

    N = data["payoff"]["N"]
    D = data["payoff"]["D"]
    p = data["payoff"]["p"]
    board = Board(5, 5, 0, N, D, p)

    bStats = []
    cStats = []
    sStats = []
    for x in range(numExperiments):
        batchResult = batchRun(board, numScientists, numRuns, data)
        bStats.append(batchResult[0])
        cStats.append(batchResult[1])
        sStats.append(batchResult[2])

    # write stats to csv output file
    # each experiment's stats appear in one row
    boardStats = "boardStats.csv"
    with open(boardStats, 'w', newline='') as file:
        writer = csv.writer(file)
        header = ['Percentage Payoff Discovered', 'Attrition']
        writer.writerow(header)
        writer.writerows(bStats)

    cellStats = "cellStats.csv"
    with open(cellStats, 'w', newline='') as file:
        writer = csv.writer(file)
        header = ['Funds', 'Payoff Extracted']
        writer.writerow(header)
        writer.writerows(cStats)
    
    sciStats = "sciStats.csv"
    with open(sciStats, 'w', newline='') as file:
        writer = csv.writer(file)
        header = ['Total Funding Accumulated', 'starFactor', 'Citation Count']
        writer.writerow(header)
        writer.writerows(sStats)
    return
