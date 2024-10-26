## Simulating Science
# Purpose
This code simulates scientists exploring the scientific research space. 

# Running the Simulation
In the file default.json, you may change the default parameters. 

1. Open ipython and navigate to the correct directory.

2. Commands are written to indicate the parameter value you want to vary from default.json as such:
```
[paramType] [param] [newValue]
```
Example of one sequence of commands:
```
Example:
cellChoiceWeights citation 1
fundDistributionFactors numHits 0.5
```

Create a text file containing a list of commands to run, with each paragraph indicating one sequence of experiments and each line of the paragraph indicating the change. 

```
scientistIncentives citation 0
scientistIncentives payoff 0.33
scientistIncentives exploration 0.33
scientistIncentives funding 0.33

scientistIncentives citation 0.1
scientistIncentives payoff 0.33
scientistIncentives exploration 0.3
scientistIncentives funding 0.3

...
```

3. Run autoExperiment to begin the experiments.
```python
run autoExperiment.py
```

4. Follow the input prompts to run experiments. Example inputs are as such:
```
Parameters file path: commands/testing.txt
Experiment parameters with format (numScientists, numRuns, numExperiments, boardDimension): (20, 50, 100, 5)
Output folder path: testing
```

5. To repeat runs, please quit and restart ipython and proceed from Step 1 again. 
This ensures the database connection is refreshed

# Outputs
Three csv files and one database file will be generated into the output folder path. The files are: boardStats.csv, cellStats.csv, sciStats.csv, and data.db. 

boardStats.csv: Percentage Payoff Discovered, Attrition, Attrition Rate
cellStats.csv: Input, Location, Funds, Payoff Extracted, Remaining Payoff, Total Payoff
sciStats: Input, ID, Total Funding Accumulated, starFactor, Citation Count
data.db: A database containing detailed information of all three above, and including more information to replicate the experiment. 

# Generating Figures
To generate an animation of each batchRun, uncomment the second to last line in the oneRun funciton in Run.py.
Note that you may need to install packages like latextable if you want to perform certain functions like generating LaTeX figures.

# Additional Help
If more clarification is needed, feel free to contact the AMISTAD Lab at Harvey Mudd College.
