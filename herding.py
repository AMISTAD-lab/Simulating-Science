import sqlite3
import pandas as pd
import numpy as np
from scipy.stats import pearsonr

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

def remainingPayoffExtraction():
    '''
    Extracts raw payoff values (not proportions) for each time step per experiment.
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

    # Initialize payoff results across all input strings
    all_payoff_results = []

    # Iterate over each unique inputStr value
    for input_str in input_str_values:
        # Filter data for the current inputStr
        input_str_data = df[df['inputStr'] == input_str]

        # Get unique experiments
        experiments = input_str_data['numExperiment'].unique()

        for experiment in experiments:
            # Filter data for the current experiment
            exp_data = input_str_data[input_str_data['numExperiment'] == experiment]
            
            # Get unique time steps for the current experiment
            time_steps = exp_data['timeStep'].unique()

            # Track previous cumulative payoff to compute incremental payoffs
            previous_payoff = 0

            # Iterate over time steps to calculate the raw payoff at each time step
            for time_step in time_steps:
                # Sum totalPayoffExtracted for the current time step
                total_payoff_at_step = exp_data[exp_data['timeStep'] == time_step]['totalPayoffExtracted'].sum()

                # Calculate the incremental payoff at this step
                payoff_extracted_at_step = total_payoff_at_step - previous_payoff
                previous_payoff = total_payoff_at_step

                # Append the raw payoff result (not proportion) for this time step
                all_payoff_results.append([experiment, time_step, payoff_extracted_at_step])

    # Create DataFrame from raw payoff results
    df_payoff_results = pd.DataFrame(all_payoff_results, columns=['Experiment', 'Time Step', 'Raw Payoff'])

    # Optionally, write the results to CSV for further analysis
    df_payoff_results.to_csv('raw_payoff_per_time_step.csv', index=False)

    return df_payoff_results

from scipy.stats import pearsonr
import numpy as np
import pandas as pd
import sqlite3

def queriesExtraction():
    '''
    Produces numpy 2D arrays to run the herding function on corresponding to each
    time step, calculates Pearson correlation between herding and payoff values,
    and outputs Pearson correlation, p-value, and 95% confidence intervals.
    '''
    # Connect to the database
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

    # Load the raw payoff values per time step (from remainingPayoffExtraction)
    df_payoff_results = pd.read_csv('raw_payoff_per_time_step.csv')

    # Get unique inputStr values
    input_str_values = df['inputStr'].unique()

    # Initialize correlation results list
    correlation_results = []

    for input_str in input_str_values:
        # Filter data for the current inputStr
        input_str_data = df[df['inputStr'] == input_str]

        # Get unique experiments and locations
        experiments = input_str_data['numExperiment'].unique()
        locations = input_str_data['location'].unique()

        # Map locations to indices
        location_to_index = {loc: idx for idx, loc in enumerate(locations)}

        # **Re-initialize herding_results list for each inputStr**
        herding_results = []

        for experiment in experiments:
            # Filter data for the current experiment
            exp_data = input_str_data[input_str_data['numExperiment'] == experiment]
            
            # Get unique time steps for the current experiment
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
                herding_results.append([experiment, time_step, input_str, herding_result[0], herding_result[1], herding_result[2]])

        # Convert herding results to DataFrame
        df_herding_results = pd.DataFrame(herding_results, columns=['Experiment', 'Time Step', 'Input String', 'Uniform Entropy', 'Board Entropy', 'Herding'])

        # Save herding results to CSV for this inputStr only
        filename = f'QUERIES_{input_str}.csv'
        df_herding_results.to_csv(filename, index=False)

        # Merge herding results with raw payoff values by Experiment and Time Step
        df_combined = pd.merge(df_herding_results, df_payoff_results, on=['Experiment', 'Time Step'])

        # Calculate Pearson correlation between Herding and Raw Payoff values
        correlation, p_value = pearsonr(df_combined['Herding'], df_combined['Raw Payoff'])

        # Calculate 95% confidence interval for Pearson correlation
        n = len(df_combined)  # sample size
        if n > 2:  # Ensure there are enough data points for meaningful correlation
            # Standard error of the correlation
            se_r = np.sqrt((1 - correlation ** 2) / (n - 2))

            # 95% confidence interval
            z = 1.96  # Z-score for 95% confidence
            ci_lower = correlation - z * se_r
            ci_upper = correlation + z * se_r
        else:
            ci_lower, ci_upper = np.nan, np.nan

        # Append Pearson correlation results for this input_str, along with CI
        correlation_results.append([input_str, correlation, p_value, ci_lower, ci_upper])

    # Convert correlation results to DataFrame and save to CSV
    df_correlation_results = pd.DataFrame(correlation_results, columns=['Input String', 'Pearson Correlation', 'p-value', 'CI Lower', 'CI Upper'])
    df_correlation_results.to_csv('pearson_correlation_results_with_CI.csv', index=False)

    return df_herding_results, df_correlation_results
