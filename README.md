## Simulating Science
# Purpose
This code simulates scientists exploring the scientific research space.

# Getting Started
In the file default.json, you may change the default parameters. 

To run the experiment, open ipython in your terminal, then enter the following commands, replacing with desired parameters: 

run experiment

experiment(numScientists, numRuns, numExperiments, boardDimension)

The terminal will prompt you to enter any other specific parameters changing the default settings, or you can press enter again and the simulation will run with the default parameters. If you do want to specify additional parameter settings, you model each new line with a new parameter after the default file. For instance, you may enter: 

scientistIncentives citation 1

fundFactors visPayoff 0.5

To generate an animation of each batchRun, uncomment the second to last line in the oneRun funciton in Run.py.
Note that you may need to install packages like latextable if you want to perform certain functions like generating LaTeX figures.

# Additional Help
If more clarification is needed, feel free to contact the AMISTAD Lab at Harvey Mudd College.
