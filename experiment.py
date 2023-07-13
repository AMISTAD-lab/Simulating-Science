import json
import csv
import sqlite3
import latextable
import pandas as pd
import os
import statistics
from tabulate import tabulate
from texttable import Texttable
from Run import *

csv_files = []

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

def plot_confidence_interval(x, values, z=1.96, color='#2187bb', horizontal_line_width=0.25):
   mean = statistics.mean(values)
   stdev = statistics.stdev(values)
   confidence_interval = z * stdev / math.sqrt(len(values))


   left = x - horizontal_line_width / 2
   top = mean - confidence_interval
   right = x + horizontal_line_width / 2
   bottom = mean + confidence_interval
   plt.plot([x, x], [top, bottom], color=color)
   plt.plot([left, right], [top, top], color=color)
   plt.plot([left, right], [bottom, bottom], color=color)
   plt.plot(x, mean, 'o', color='#f44336')


   return mean, confidence_interval

def generateLineGraph(listOfFolders):
    payoffs = []
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
                    payoffs.append(data['Percentage Payoff Discovered'].tolist())
                    attrRate = data['Attrition Rate'].tolist()
                elif file == 'sciStats.csv':
                    sciFund = data['Total Funding Accumulated'].tolist()
                    sciCitCount = data['Citation Count'].tolist()
    plt.xticks([1, 2, 3, 4, 5], ['0.2', '0.4', '0.6', '0.8', '1'])
    plt.title('Payoffs')
    plot_confidence_interval(1, payoffs[0])
    plot_confidence_interval(2, payoffs[1])
    plot_confidence_interval(3, payoffs[2])
    plot_confidence_interval(4, payoffs[3])
    plot_confidence_interval(5, payoffs[4])
    plt.show()
    return
    
def generateLaTeX(listOfFolders):
    """
    Outputs LaTeX code to generate tables with simulation statistics.
    Takes in a list of csv file names within folders in the repository.
    """
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
    
def generateBarGraph(csv_file, x_tick_labels=None, legend_labels = None):
    #empty lists to hold the data for each CSV file
    all_data = []
    all_averages = []
    all_variances = []

    #colors for the bars
    colors = ['blue', 'green', 'purple'] #orange, red

    for csv_file in csv_files:
        #Read the CSV file
        df = pd.read_csv(csv_file)

        #Extract the first column (payoff in boardStats)
        column = df.iloc[:, 0]

        #average and variance of the column
        average = column.mean()
        variance = column.var()

        #Append the average and variance to the lists
        all_averages.append(average)
        all_variances.append(variance)

        #Append the average to the data list
        all_data.append(average)

    #create bar graph
    num_files = len(csv_files)
    num_bars = num_files // 3
    x = np.arange(num_bars)

    #width of each bar
    width = 0.2
    bar_positions = [x - width + width * i for i in range(3)]

    fig, ax = plt.subplots()

    #Plot the bars
    for i, position in enumerate(bar_positions):
        bars = ax.bar(position, all_data[i::3], width=width, yerr=np.sqrt(all_variances[i::3]), capsize=4, color=colors[i], label=f'Bar Group {i+1}')

    #show exact values of each bar(comment out)
    # for i, position in enumerate(bar_positions):
    #     for j, val in enumerate(all_data[i::3]):
    #         ax.text(position[j], val, str(val), ha='center', va='bottom')

    #Remove x-axis ticks
    ax.tick_params(axis='x', which='both', bottom=False, top=False)

    #Set the x-axis ticks and labels
    if x_tick_labels:
        assert len(x_tick_labels) == num_bars, "Number of x tick labels must match the number of bars."
        ax.set_xticks(x)
        ax.set_xticklabels(x_tick_labels)
    else:
        ax.set_xticks(x)
        ax.set_xticklabels(['Group {}'.format(i + 1) for i in range(num_bars)])

    #x-axis label
    ax.set_xlabel('Scientist Incentives')

    #y-axis label
    ax.set_ylabel('Average Payoff')

    #legend
    if legend_labels:
        assert len(legend_labels) == 3, "Number of legend labels must match the number of bar groups (3)."
        handles, _ = ax.get_legend_handles_labels()
        ax.legend(handles, legend_labels)

    #Display the graph
    plt.show()

def callBarGraph():
    x_tick_labels = []
    legend_labels = []

    condition = True
    print("input csv files")
    while condition:
        userFiles = str(input())
        if userFiles == '':
            condition2 = True
            print("input x labels")
            while condition2:
                userXLabels = str(input())
                if userXLabels == '':
                    condition3 = True
                    print("input legend labels")
                    while condition3:
                        userLegend = str(input())
                        if userLegend == '':
                            condition3 = False
                            condition2 = False
                            condition = False
                        else:
                            legend_labels.append(userLegend)
                else:
                    x_tick_labels.append(userXLabels)
        else:
            csv_files.append(userFiles)

    generateBarGraph(csv_files, x_tick_labels, legend_labels)
