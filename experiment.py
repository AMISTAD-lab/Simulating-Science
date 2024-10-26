import json
import csv
import sqlite3
import latextable
import pandas as pd
import os
import statistics
import scipy.special
from tabulate import tabulate
from texttable import Texttable
from Run import *

def chk_conn(conn):
    '''Checks if csv connection exists'''
    try:
        conn.cursor()
        return True
    except Exception as ex:
        return False

def openConn():
    '''Opens conection to csv using default.json and predefined schema for board (b), cells (c), and scientists (s)'''
    csv_files = []
    inp = "default.json"
    with open(inp, "r") as params:
        data = json.load(params)

    # setting up sql database connection
    conn = sqlite3.connect('data.db')

    # Define the database schema
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
                        numExperiment INTEGER,
                        timeStep INTEGER,
                        location STRING,
                        totalFunds FLOAT,
                        totalPayoffExtracted FLOAT,
                        numQueries INTEGER,
                        uniqIds STRING
                    )''')

    conn.execute('''CREATE TABLE IF NOT EXISTS sStats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        inputStr STRING,
                        numExperiment INTEGER,
                        timeStep INTEGER,
                        uniqId INTEGER,
                        totalFunds FLOAT,
                        starFactor FLOAT,
                        totalCitations INTEGER,
                        totalImpact FLOAT,
                        cellQueried STRING
                    )''')

    conn.execute('''CREATE TABLE IF NOT EXISTS runStats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        inputStrSci STRING,
                        numExpSci INTEGER,
                        timeStepSci INTEGER,
                        inputStrCell STRING,
                        numExpCell INTEGER,
                        timeStepCell INTEGER,
                        numCellsHit INTEGER,
                        FOREIGN KEY (inputStrSci) REFERENCES sStats(inputStr),
                        FOREIGN KEY (numExpSci) REFERENCES sStats(numExperiment),
                        FOREIGN KEY (timeStepSci) REFERENCES sStats(timeStep),
                        FOREIGN KEY (inputStrCell) REFERENCES cStats(inputStr),
                        FOREIGN KEY (numExpCell) REFERENCES cStats(numExperiment),
                        FOREIGN KEY (timeStepCell) REFERENCES cStats(timeStep)
                    )''')
    conn.commit()
    return conn, data

def writeBStats(inputStr, bStats):
    '''Compiles board data to be written for each experiment'''
    insert_query = "INSERT INTO bStats (inputStr, payoffExtracted, attrition, attritionRate) VALUES (?, ?, ?, ?)"
    values = (inputStr, bStats[0], bStats[1], bStats[2])
    conn.execute(insert_query, values)
    conn.commit()

def experiment(numScientists, numRuns, numExperiments, boardDimension, newInput):
    """
    Uses inputs to execute a number of years of simulation (numRuns), repeated numExperiments times
    Inputs: 
        int: numScientists, numRuns, numExperiments, boardDimension
        string: newInput, from the autoExperiment commands
    """
    conn, data = openConn() # Open connection to csv 

    # Parses through given command input and error checks
    fullInput = []
    for inputStr in newInput:
        if len(inputStr.split()) == 3:
            typeParam = inputStr.split()[0]
            param = inputStr.split()[1]
            newNum = float(inputStr.split()[2])
            if typeParam in data.keys() and param in data[typeParam].keys():
                data[typeParam][param] = newNum
                fullInput.append(inputStr)
            else:
                print("Parameter you entered does not follow the default style", typeParam, param)
                return
        else:
            print("Check input format - input must be of different length")
            return
    fullInput = ", ".join(fullInput)

    # Defines default.json variables
    N = data["payoffExtraction"]["N"]
    D = data["payoffExtraction"]["D"]
    p = data["payoffExtraction"]["p"]
    probZero = data["zeroPayoff"]["probability"]

    # Defines data to be input into csv's
    bStats = []
    cStats = []
    sStats = []
    currentScientist = 0
    # Gathers data from each experiment
    for x in range(numExperiments):
        board = Board(boardDimension, boardDimension, probZero, N, D, p)
        currentScientist, batchResult = batchRun(board, numScientists, numRuns, data, fullInput, x+1, currentScientist)
        bStats.append(batchResult[0])
        cStats.append(batchResult[1])
        sStats.append(batchResult[2])
        writeBStats(fullInput, bStats[x])

    # Write data into csv files
    # Each row of data encompasses one experiment
    boardStats = "boardStats.csv"
    with open(boardStats, 'w', newline='') as file:
        writer = csv.writer(file)
        header = ['Percentage Payoff Discovered', 'Attrition', 'Attrition Rate']
        writer.writerow(header)
        writer.writerows(bStats)

    cellStats = "cellStats.csv"
    with open(cellStats, 'w', newline='') as file:
        writer = csv.writer(file)
        header = ['Input', 'Location', 'Funds', 'Payoff Extracted', 'Remaining Payoff', 'Total Payoff']
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
                if file == 'boardStats.csv':
                    payoffs.append(data['Percentage Payoff Discovered'].tolist())
    plt.xticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        ['0.0', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1.0'])
    plt.xlabel('Parameter Weight')
    plt.ylabel('Average Percentage Payoff Discovered')
    plot_confidence_interval(1, payoffs[0])
    plot_confidence_interval(2, payoffs[1])
    plot_confidence_interval(3, payoffs[2])
    plot_confidence_interval(4, payoffs[3])
    plot_confidence_interval(5, payoffs[4])
    plot_confidence_interval(6, payoffs[5])
    plot_confidence_interval(7, payoffs[6])
    plot_confidence_interval(8, payoffs[7])
    plot_confidence_interval(9, payoffs[8])
    plot_confidence_interval(10, payoffs[9])
    # plot_confidence_interval(11, payoffs[10])

    plt.show()
    return
    
def generateLaTeX(listOfFolders):
    """
    Outputs LaTeX code to generate tables with simulation statistics.
    Takes in a list of csv file names within folders in the repository.
    Enter in the default parameters file first, as a point of reference for the
    other statistics. 
    """
    boardRows = [['\\textbf{Input}', '\\textbf{Percentage of Payoff Discovered}', '\\textbf{Attrition Rate}']]
    # cellRows = [['\\textbf{Input}', '\\textbf{Difference between Funding and Payoff Extracted : Default}']]
    # sciRows = [['\\textbf{Input}', '\\textbf{Difference between Funding and Citation Count : Default}']]
    cellRows = [['\\textbf{Input}', '\\textbf{Average Difference}', '\\textbf{Difference Ratio}']]
    sciRows = [['\\textbf{Input}', '\\textbf{Average Difference}', '\\textbf{Difference Ratio}']]
    defaultVals = {"avgPayoffToFund" : 1, "CIavgPayoffToFund" : 1,
                        "avgCitCountToFund" : 1, "CIavgCitCountToFund" : 1}
    for i in range(len(listOfFolders)):
        folder = listOfFolders[i]
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

        if i == 0:
            defaultVals = {"avgPayoffToFund" : avgPayoffToFund, "CIavgPayoffToFund" : CIavgPayoffToFund,
                            "avgCitCountToFund" : avgCitCountToFund, "CIavgCitCountToFund" : CIavgCitCountToFund}

        if type(inputStr[0]) == str:
            boardRows.append([inputStr[0],
                str(f'{avgPayoff:0.3f}') + "\hphantom{7} $\pm$ " + str(f'{CIPayoff:0.3f}'),
                str(f'{avgAttrRate:0.3f}') + "\hphantom{7} $\pm$ " + str(f'{CIAttrRate:0.3f}')])
            cellRows.append([inputStr[0],
                str(f'{avgPayoffToFund:0.3f}') + "\hphantom{7} $\pm$ " + str(f'{CIavgPayoffToFund:0.3f}'),
                str(f'{avgPayoffToFund / defaultVals["avgPayoffToFund"]:0.3f}')])
            sciRows.append([inputStr[0],
                str(f'{avgCitCountToFund:0.3f}') + "\hphantom{7} $\pm$ " + str(f'{CIavgCitCountToFund:0.3f}'),
                str(f'{avgCitCountToFund / defaultVals["avgCitCountToFund"]:0.3f}')])
        else:
            boardRows.append(["Default (uniformly weighted)",
                str(f'{avgPayoff:0.3f}') + "\hphantom{7} $\pm$ " + str(f'{CIPayoff:0.3f}'),
                str(f'{avgAttrRate:0.3f}') + "\hphantom{7} $\pm$ " + str(f'{CIAttrRate:0.3f}')])
            cellRows.append(["Default (uniformly weighted)",
                str(f'{avgPayoffToFund:0.3f}') + "\hphantom{7} $\pm$ " + str(f'{CIavgPayoffToFund:0.3f}'),
                str(f'{avgPayoffToFund / defaultVals["avgPayoffToFund"]:0.3f}')])
            sciRows.append(["Default (uniformly weighted)",
                str(f'{avgCitCountToFund:0.3f}') + "\hphantom{7} $\pm$ " + str(f'{CIavgCitCountToFund:0.3f}'),
                str(f'{avgCitCountToFund / defaultVals["avgCitCountToFund"]:0.3f}')])

    # Code inspired by https://colab.research.google.com/drive/1Iq10lHznMngg1-Uoo-QtpTPii1JDYSQA?usp=sharing#scrollTo=K7NNR1Vg40Vo
    table = Texttable()
    table.set_cols_align(["c"] * 3)
    table.set_deco(Texttable.HEADER | Texttable.VLINES)
    table.add_rows(boardRows)

    tabulate(boardRows, headers='firstrow', tablefmt='latex')
    print(latextable.draw_latex(table))

    table = Texttable()
    table.set_cols_align(["c"] * 3)
    table.set_deco(Texttable.HEADER | Texttable.VLINES)
    table.add_rows(cellRows)

    tabulate(cellRows, headers='firstrow', tablefmt='latex')
    print(latextable.draw_latex(table))

    table = Texttable()
    table.set_cols_align(["c"] * 3)
    table.set_deco(Texttable.HEADER | Texttable.VLINES)
    table.add_rows(sciRows)

    tabulate(sciRows, headers='firstrow', tablefmt='latex')
    print(latextable.draw_latex(table))

    return
    
def generateBarGraph(csv_files, x_tick_labels=None, legend_labels=None):
    #empty lists to hold the data for each CSV file
    all_data = []
    all_averages = []
    all_variances = []

    #colors for the bars
    colors = ['#016528', '#64b46c', '#bee5b8']

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
    csv_files = []
    x_tick_labels = []
    legend_labels = []

    print("Input CSV files (press Enter without input to finish):")
    while True:
        userFiles = str(input())
        if userFiles == '':
            break
        csv_files.append(userFiles)

    print("Input x-axis labels (press Enter without input to finish):")
    while True:
        userXLabels = str(input())
        if userXLabels == '':
            break
        x_tick_labels.append(userXLabels)

    print("Input legend labels (press Enter without input to finish):")
    while True:
        userLegend = str(input())
        if userLegend == '':
            break
        legend_labels.append(userLegend)

    generateBarGraph(csv_files, x_tick_labels, legend_labels)


def generateKL(file, numScientists, boardDimensions, numRuns, numExperiments):
    """generates the KL divergence per run between the uniform spread of scientists and the actual run to measure herding"""
    
    conn = sqlite3.connect(file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cStats")

    # P is the ideal distribution
    P = [(numScientists/(boardDimensions * boardDimensions))] * (boardDimensions * boardDimensions)
    Q = []
    KL = []
    id = 1
    while id <= (numRuns * numExperiments): 
        sql_numQueries = "SELECT numQueries FROM cStats WHERE ID = " + str(id) + ";" 
        cursor.execute(sql_numQueries)
        numQueries = cursor.fetchall()
        numQueries = int(numQueries[0][0])

        sql_location = "SELECT location FROM cStats WHERE ID = " + str(id) + ";"
        cursor.execute(sql_location)
        location = cursor.fetchall()
        location = (int(location[0][0][1]), int(location[0][0][4]))

        sql_numExperiment = "SELECT numExperiment FROM cStats WHERE ID = " + str(id) + ";"
        cursor.execute(sql_numExperiment)
        numExperiment = cursor.fetchall()
        numExperiment = int(numExperiment[0][0])

        sql_timeStep = "SELECT timeStep FROM cStats WHERE ID = " + str(id) + ";"
        cursor.execute(sql_timeStep)
        timeStep = cursor.fetchall()
        timeStep = int(timeStep[0][0])

        Q += [numQueries/numScientists]
        if location == (boardDimensions-1, boardDimensions-1): #if we have boardDimensions^2 cells in our list
            KL += (numExperiment, timeStep, scipy.special.kl_div(P, Q))
            Q = []

        id += 1

    cursor.close()
    conn.close()
    return KL
