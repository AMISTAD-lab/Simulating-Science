from altExperiment import *
import os
import shutil

'''
USAGE: 
- To run several experiments at once, as a batch of experiments.
- Saves board, cell, sci stats for each experiment
- Only saves one data.db file for all experiments run, so make sure to separate each batch according to how you want the data.db data to be separated. 

HOW TO USE THE AUTO EXP RUNNER:
- Create or use a txt file under commands folder in the same format
- param (string): the scientist incentive (payoff, citation, exploration, funding, citationExtra, testing)
- target_path (string): target directory to put stats.csv files into
- do:
    run autoAltExp.py

Note: 
- After running autoAltExp.py each time, quit ipython and run again. 
- This makes sure the database connection is for the new, correct one and not the one that's been moved.
'''

param = "payoff"
file_path = "commands/" + param + ".txt"
with open(file_path, 'r') as file:
        contents = file.read()

def copy_file_to_folder(file_path, target_folder_name):
    """
    Copies a file and moves the copy into a specified folder in the same directory.
    
    Args:
    - file_path (str): The path of the file to copy.
    - target_folder_name (str): The name of the target folder.
    
    Returns:
    - str: The path to the copied file, or an error message if something went wrong.
    """
    try:
        # Get the directory and file name from the given file path
        directory = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        
        # Define the target directory
        target_directory = os.path.join(directory, target_folder_name)
        
        # Create the target directory if it doesn't exist
        if not os.path.exists(target_directory):
            os.makedirs(target_directory)
        
        # Define the target file path
        target_file_path = os.path.join(target_directory, file_name)
        
        # Copy the file to the target directory
        shutil.copy2(file_path, target_file_path)
        
        return f"Copied {file_path} to {target_file_path}"
    except FileNotFoundError:
        return f"File not found: {file_path}"
    except Exception as e:
        return f"An error occurred: {e}"

def parse_scientist_incentives(text):
    paragraphs = text.strip().split('\n\n')
    parsed_result = [paragraph.split('\n') for paragraph in paragraphs]
    return parsed_result
result = parse_scientist_incentives(contents)

for i in range(len(result)):
    paragraph = result[i]
    title = paragraph[0].split()[1] + paragraph[0].split()[2]
    # experiment(1, 1, 1, 5, paragraph)
    experiment(50, 50, 100, 10, paragraph)
    print("YAY!! " + str(i+1) + "/" + str(len(result)) + " " + title)
    
    # Makes a copy of stats.csv files and moves it to the target directory
    target_path = "(softmax)/10x10/" + paragraph[0].split()[1] + "/" + title
    copy_file_to_folder("boardStats.csv", target_path)
    copy_file_to_folder("cellStats.csv", target_path)
    copy_file_to_folder("sciStats.csv", target_path)

# Moves data.db to target directory and creates a new, empty data.db
shutil.move("data.db", ("(softmax)/10x10/" + param))
open("data.db", 'w')