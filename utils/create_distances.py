import pandas as pd
from itertools import combinations

from utils import calculate_distance


if __name__ == "_main__":
    offload = pd.read_csv('../data/offload.csv')
    inputs = pd.read_csv('../data/inputs.csv')

    all_data = pd.concat([offload, inputs])
    all_data.reset_index(drop=True, inplace=True)
    size = all_data.shape[0]

    indexes = list(range(size))

    tuples = list(combinations(indexes, 2))

    distances = list(map(lambda x: calculate_distance(all_data, x), tuples))
    distances_dataframe = pd.DataFrame(distances, columns=['from', 'to', 'distance'])
    distances_dataframe.to_csv('data/distances.csv', index=False)
