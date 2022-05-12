import os
from itertools import combinations

import pandas as pd

from utils import get_distance

dir_path = os.path.dirname(os.path.abspath(__file__))
base_path = os.path.join(dir_path, '..', 'data')

offload_data_path = os.path.join(base_path, 'offload.csv')
input_data_path = os.path.join(base_path, 'inputs.csv')
distances_save_path = os.path.join(base_path, 'distances.csv')

if __name__ == "__main__":
    offload = pd.read_csv(offload_data_path)
    inputs = pd.read_csv(input_data_path)

    all_data = pd.concat([offload, inputs])
    all_data.reset_index(drop=True, inplace=True)
    size = all_data.shape[0]

    indexes = list(range(size))

    tuples = list(combinations(indexes, 2))

    distances = list(map(lambda x: get_distance(all_data, x), tuples))
    distances_dataframe = pd.DataFrame(distances, columns=['from', 'to', 'distance'])
    distances_dataframe.to_csv(distances_save_path, index=False)
