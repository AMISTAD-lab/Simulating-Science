import sqlite3
import pandas as pd
import numpy as np
def entropy(probabilities):
    probs = probabilities[probabilities > 0]
    return -np.sum(probs * np.log2(probs), axis=0)

def herding(cell_counts_vector):
    """ Input: cell_counts_vector is a numpy vector where each index corresponds 
            to the number of scientists currently in that cell. 
    
        Output: a tuple of the uniform entropy (which is maximum entropy for this
            number of scientists on this board size if we allow fractional scientists,
            board entropy, and a herding value between 0 and 1, which is maximum herding,
            namely, all scientists in a single cell.
    """
    total = np.sum(cell_counts_vector)
    uniform_vector = np.ones(cell_counts_vector.size) * (total / cell_counts_vector.size)
    uniform_entropy = entropy(uniform_vector / total)
    entr = entropy(cell_counts_vector / total)
    return (uniform_entropy, entr, 1 - entr/uniform_entropy)


if __name__ == "__main__":
    #=============
    # Test 
    #=============
    num_of_subareas = 10
    vec = np.random.randint(0, 20, num_of_subareas)
    print(f"Vector: {vec}")
    (unif, entr, herd) = herding(vec)
    print(f"Uniform Entropy: {unif}, Board Entropy: {entr}, Herding: {herd}")

    # Case when all scientists are in a single cell. Making sure our herding metric makes sense.
    total = np.sum(vec)
    vec = np.zeros(num_of_subareas)
    vec[0] = total
    print(f"Vector 2: {vec}")
    (unif, entr, herd) = herding(vec)
    print(f"Uniform Entropy: {unif}, Board Entropy: {entr}, Herding: {herd}")

    # Case when all (fractional) scientists are distributed evenly (maximum entropy board).
    vec = np.ones(num_of_subareas) * (total / num_of_subareas)
    print(f"Vector 3: {vec}")
    (unif, entr, herd) = herding(vec)
    print(f"Uniform Entropy: {unif}, Board Entropy: {entr}, Herding: {herd}")

def oldCsvDataExtraction():
    '''
    Extracts total payoff for each cell for a given experiment and writes
    the herding function output to a single CSV file with headers.
    '''
    # Read the CSV file into a DataFrame
    df = pd.read_csv('cellStats.csv')

    # Initialize variables
    arrays = []
    current_array = None
    results = []

    def parse_location(location_str):
        # Convert the location string to a tuple of integers
        return tuple(map(int, location_str.strip("()").split(", ")))

    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        # Extract and parse the cell location
        location = parse_location(row['Location'])
        
        # Extract the Total Payoff value
        total_payoff = row['Total Payoff']
        
        # Check if we need to start a new array
        if location == (0, 0):
            if current_array is not None:
                arrays.append(current_array)
                # Compute herding result and store it with headers
                herding_result = herding(current_array)
                results.append(['Array {}'.format(len(arrays)), herding_result[0], herding_result[1], herding_result[2]])
            # Determine the size of the new array
            current_array = np.zeros((10, 10))  # You might need to adjust this size based on your data
        
        # Update the current array with the Total Payoff value
        if current_array is not None:
            # Ensure the array is large enough for the location
            max_x, max_y = max(location[0], current_array.shape[0] - 1), max(location[1], current_array.shape[1] - 1)
            if max_x >= current_array.shape[0] or max_y >= current_array.shape[1]:
                # Resize the array if necessary
                new_shape = (max_x + 1, max_y + 1)
                new_array = np.zeros(new_shape)
                new_array[:current_array.shape[0], :current_array.shape[1]] = current_array
                current_array = new_array
            current_array[location] = total_payoff

    # Append the last array if it exists
    if current_array is not None:
        arrays.append(current_array)
        # Compute herding result and store it with headers
        herding_result = herding(current_array)
        results.append(['Array {}'.format(len(arrays)), herding_result[0], herding_result[1], herding_result[2]])

    # Create DataFrame from results
    df_results = pd.DataFrame(results, columns=['Experiment', 'Uniform Entropy', 'Board Entropy', 'Herding'])

    # Write to CSV
    df_results.to_csv('herding_results.csv', index=False)

def oldSqlDataExtraction(): 
    '''
    Produces numpy 2D arrays to run the herding function on corresponding to each
    time step. Writes the herding function output to separate CSV files based on the
    inputStr value.
    '''
    # Connect to the database (modify the connection string as needed)
    conn = sqlite3.connect('data.db')

    # Query to get the data
    query = """
    SELECT numExperiment, location, timeStep, numQueries, inputStr
    FROM cStats
    ORDER BY inputStr, numExperiment, timeStep, location
    """

    # Load the data into a Pandas DataFrame
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Get unique inputStr values
    input_str_values = df['inputStr'].unique()

    # Iterate over each unique inputStr value
    for input_str in input_str_values:
        # Filter data for the current inputStr
        input_str_data = df[df['inputStr'] == input_str]

        # Get unique experiments and locations
        experiments = input_str_data['numExperiment'].unique()
        locations = input_str_data['location'].unique()

        # Map locations to indices
        location_to_index = {loc: idx for idx, loc in enumerate(locations)}

        # Initialize dictionaries to store cumulative sums and counts
        cumulative_sums = {}
        counts = {}

        # Initialize results list
        results = []

        for experiment in experiments:
            # Filter data for the current experiment
            exp_data = input_str_data[input_str_data['numExperiment'] == experiment]
            
            # Get unique timeSteps for the current experiment
            time_steps = exp_data['timeStep'].unique()
            
            for time_step in time_steps:
                # Filter data for the current timeStep
                ts_data = exp_data[exp_data['timeStep'] == time_step]
                
                # Initialize arrays if they don't exist for this time step
                if time_step not in cumulative_sums:
                    cumulative_sums[time_step] = np.zeros(len(locations))
                    counts[time_step] = np.zeros(len(locations))
                
                for _, row in ts_data.iterrows():
                    location_index = location_to_index[row['location']]
                    num_queries = row['numQueries']
                    
                    cumulative_sums[time_step][location_index] += num_queries
                    counts[time_step][location_index] += 1
        
        # Calculate averages and write results to CSV
        results = []
        for time_step in sorted(cumulative_sums.keys()):
            average_array = cumulative_sums[time_step] / counts[time_step]
            herding_result = herding(average_array)
            results.append([time_step, herding_result[0], herding_result[1], herding_result[2]])

        # Create DataFrame from results
        df_results = pd.DataFrame(results, columns=['Time Step', 'Uniform Entrop', 'Board Entropy', 'Herding'])

        # Write to CSV with inputStr value in the filename
        filename = f'{input_str}.csv'
        df_results.to_csv(filename, index=False)

def remainingPayoffExtraction():
    '''
    Analyzes how concentrated payoff is across time steps for each experiment.
    For each experiment, calculates the proportion of the final totalPayoffExtracted at each time step
    and writes the herding function output to separate CSV files based on the inputStr value.
    '''
    # Connect to the database
    conn = sqlite3.connect('data.db')

    # Query to get the data
    query = """
    SELECT numExperiment, timeStep, totalPayoffExtracted, inputStr
    FROM cStats
    ORDER BY inputStr, numExperiment, timeStep
    """

    # Load the data into a Pandas DataFrame
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Get unique inputStr values
    input_str_values = df['inputStr'].unique()

    # Iterate over each unique inputStr value
    for input_str in input_str_values:
        # Filter data for the current inputStr
        input_str_data = df[df['inputStr'] == input_str]

        # Get unique experiments
        experiments = input_str_data['numExperiment'].unique()

        # Initialize results list
        results = []

        for experiment in experiments:
            # Filter data for the current experiment
            exp_data = input_str_data[input_str_data['numExperiment'] == experiment]
            
            # Get unique time steps for the current experiment
            time_steps = exp_data['timeStep'].unique()

            # Find the last time step
            last_time_step = time_steps.max()

            # Calculate the final total payoff extracted across all cell locations at the last time step
            final_total_payoff = exp_data[exp_data['timeStep'] == last_time_step]['totalPayoffExtracted'].sum()

            # Initialize an array to store the proportion of total payoff for each time step
            proportion_payoff_array = np.zeros(len(time_steps))

            # Now iterate over time steps to calculate the proportion of total payoff extracted for each time step
            for i, time_step in enumerate(time_steps):
                # Sum totalPayoffExtracted for the current time step
                total_payoff_at_step = exp_data[exp_data['timeStep'] == time_step]['totalPayoffExtracted'].sum()

                # Calculate the proportion of total payoff extracted at this time step relative to the final total payoff
                if final_total_payoff != 0:
                    proportion_payoff_array[i] = total_payoff_at_step / final_total_payoff
                else:
                    proportion_payoff_array[i] = 0

            # Pass the array of proportions across all time steps to the herding function once per experiment
            print(proportion_payoff_array)
            herding_result = herding(proportion_payoff_array)
            results.append([experiment, herding_result[0], herding_result[1], herding_result[2]])

        # Create DataFrame from results
        df_results = pd.DataFrame(results, columns=['Experiment', 'Uniform Entropy', 'Board Entropy', 'Herding'])

        # Write to CSV with inputStr value in the filename
        filename = f'PAYOFF_{input_str}.csv'
        df_results.to_csv(filename, index=False)


def queriesExtraction(): 
    '''
    Produces numpy 2D arrays to run the herding function on corresponding to each
    time step. Writes the herding function output to separate CSV files based on the
    inputStr value.
    '''
    # Connect to the database (modify the connection string as needed)
    conn = sqlite3.connect('data.db')

    # Query to get the data
    query = """
    SELECT numExperiment, location, timeStep, numQueries, inputStr
    FROM cStats
    ORDER BY inputStr, numExperiment, timeStep, location
    """

    # Load the data into a Pandas DataFrame
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Get unique inputStr values
    input_str_values = df['inputStr'].unique()

    # Iterate over each unique inputStr value
    for input_str in input_str_values:
        # Filter data for the current inputStr
        input_str_data = df[df['inputStr'] == input_str]

        # Get unique experiments and locations
        experiments = input_str_data['numExperiment'].unique()
        locations = input_str_data['location'].unique()

        # Map locations to indices
        location_to_index = {loc: idx for idx, loc in enumerate(locations)}

        # Initialize results list
        results = []

        for experiment in experiments:
            # Filter data for the current experiment
            exp_data = input_str_data[input_str_data['numExperiment'] == experiment]
            
            # Get unique timeSteps for the current experiment
            time_steps = exp_data['timeStep'].unique()
            
            for time_step in time_steps:
                # Filter data for the current timeStep
                ts_data = exp_data[exp_data['timeStep'] == time_step]
                
                # Initialize an array to store numQueries for the current time step
                num_queries_array = np.zeros(len(locations))
                
                for _, row in ts_data.iterrows():
                    location_index = location_to_index[row['location']]
                    num_queries_array[location_index] = row['numQueries']
                
                # Calculate herding for this time step
                herding_result = herding(num_queries_array)
                results.append([experiment, time_step, herding_result[0], herding_result[1], herding_result[2]])

        # Create DataFrame from results
        df_results = pd.DataFrame(results, columns=['Experiment', 'Time Step', 'Uniform Entropy', 'Board Entropy', 'Herding'])

        # Write to CSV with inputStr value in the filename
        filename = f'QUERIES {input_str}.csv'
        df_results.to_csv(filename, index=False)
