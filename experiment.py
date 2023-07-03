import json
import csv
import sqlite3
from Run import *

inp = "default.json"
with open(inp, "r") as params:
    data = json.load(params)

def experiment(numScientists, numRuns, numExperiments, boardDimension, ):
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
        batchResult = batchRun(board, numScientists, numRuns, data)
        bStats.append(batchResult[0])
        cStats.append(batchResult[1])
        sStats.append(batchResult[2])

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
        header = ['Location', 'Funds', 'Payoff Extracted']*(boardDimension**2)
        writer.writerow(header)
        writer.writerows(cStats)
    
    sciStats = "sciStats.csv"
    with open(sciStats, 'w', newline='') as file:
        writer = csv.writer(file)
        maxlen = len(sStats[0])
        for l in sStats:
            if len(l) > maxlen:
                maxlen = len(l)
        header = ['ID', 'Total Funding Accumulated', 'starFactor', 'Citation Count']*(maxlen//3)
        writer.writerow(header)
        writer.writerows(sStats)

    return


# setting up sql database connection
conn = sqlite3.connect('data.db')

# Define the table structure
conn.execute('''CREATE TABLE IF NOT EXISTS bStats (
                payoffExtracted FLOAT,
                attrition INTEGER,
                attritionRate FLOAT
                )''')
conn.execute('''CREATE TABLE IF NOT EXISTS cStats (
                location STRING,
                funds FLOAT,
                payoffExtracted FLOAT
                )''')
conn.execute('''CREATE TABLE IF NOT EXISTS sStats (
                uniqId INTEGER,
                totalFunding FLOAT,
                starFactor FLOAT,
                citationCount INTEGER
                )''')


with open ('boardStats.csv', 'r') as f:
    reader = csv.reader(f)
    data = next(reader) 
    query = 'insert into bStats values ({0})'
    query = query.format(','.join('?' * len(data)))
    conn.execute(query, data)
    for data in reader:
        conn.execute(query, data)
    conn.commit()
with open ('cellStats.csv', 'r') as f:
    reader = csv.reader(f)
    data = next(reader) 
    query = 'insert into cStats values ({0})'
    query = query.format(','.join('?' * len(data)))
    conn.execute(query, data)
    for data in reader:
        conn.execute(query, data)
    conn.commit()
with open ('sciStats.csv', 'r') as f:
    reader = csv.reader(f)
    data = next(reader) 
    query = 'insert into sStats values ({0})'
    query = query.format(','.join('?' * len(data)))
    conn.execute(query, data)
    for data in reader:
        conn.execute(query, data)
    conn.commit()
conn.close()
