import json
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

    N = data["payoffExtractionParams"]["N"]
    D = data["payoffExtractionParams"]["D"]
    p = data["payoffExtractionParams"]["p"]
    board = Board(5, 5, 0, N, D, p)
    for x in range(numExperiments):
        batchRun(board, numScientists, numRuns, data)
    return
