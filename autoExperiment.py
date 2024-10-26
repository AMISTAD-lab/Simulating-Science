from experiment import *
import os
import shutil

# Looks for param_path file listing the commands to change in the parameters to run the experiments
param_path = input("Parameters file path: ")
with open(param_path, 'r') as file:
    contents = file.read()
contentsParagraph = contents.strip().split('\n\n')
commandsList = [paragraph.split('\n') for paragraph in contentsParagraph]
param = param_path.split("/")[-1].split(".")[0] # Extracts the name of the param.txt file

# Asks for experiment parameters and changes to a list format
exp_params = input("Experiment parameters with format (numScientists, numRuns, numExperiments, boardDimension): ")
exp_params = exp_params.strip("()").split(", ")
exp_params = [int(x) for x in exp_params]

# Asks for output path to place files in
output_path = input("Output folder path: ") + "/"

def copy_file_to_folder(file_path, target_folder_name):
    try:
        # Get the directory and file name from the given file path
        directory = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        target_directory = os.path.join(directory, target_folder_name)
        if not os.path.exists(target_directory):
            os.makedirs(target_directory)

        # Define the target file path and copy
        target_file_path = os.path.join(target_directory, file_name)
        shutil.copy2(file_path, target_file_path)
        return
    except FileNotFoundError:
        return f"File not found: {file_path}"

for i in range(len(commandsList)):
    paragraph = commandsList[i] # Retrieves the ith command
    title = paragraph[0].split()[1] + paragraph[0].split()[2] # Creates a title for output folder name
    
    # Makes a call to experiment.py to run the experiments
    experiment(exp_params[0], exp_params[1], exp_params[2], exp_params[3], paragraph) 
    
    # Indicates the completion of each command to track progress
    print()
    print(title, "completed. " + str(i+1) + "/" + str(len(commandsList)) + " done.")
    
    # Makes a copy of stats.csv files and moves it to the target directory
    output_file_path = output_path + paragraph[0].split()[1] + "/" + title
    copy_file_to_folder("boardStats.csv", output_file_path)
    copy_file_to_folder("cellStats.csv", output_file_path)
    copy_file_to_folder("sciStats.csv", output_file_path)

# Moves data.db to output path and creates a new, empty data.db for the next batch of experiment
print(output_path + param)
shutil.move("data.db", (output_path))
open("data.db", 'w')
