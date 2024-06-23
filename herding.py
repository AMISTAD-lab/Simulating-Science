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
