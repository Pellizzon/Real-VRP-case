import os

import pandas as pd


def liter_to_bbl(volume: float) -> float:
    """Coverts volume in liters to bbl.

    Args:
        volume (float): Volume in liters.

    Returns:
        float: Volume in bbl.
    """
    output = volume * 0.00628981
    return output


def distance_to_cost(
    diesel_price: float,
    truck_consumption: float,
    dist_matrix: pd.DataFrame,
) -> pd.DataFrame:
    """Converts the distance matrix into a cost matrix.

    Args:
        diesel_price (float): Diesel cost per liter.
        truck_consumption (float): Truck's distance traveled per liter of diesel.
        dist_matrix (pd.DataFrame): Distance matrix.

    Returns:
        pd.DataFrame: Cost matrix.
    """
    ratio = diesel_price / truck_consumption
    #print(dist_matrix)
    cost_matrix = dist_matrix.copy()
    for col in dist_matrix.columns:
        cost_matrix[col] = dist_matrix[col] * ratio
    return cost_matrix


if __name__ == "__main__":

    current_path = os.path.dirname(os.path.abspath(__file__))
    distance_matrix_path = os.path.join(
        current_path, "..", "..", "data", "distance_matrix.csv"
    )

    distance_matrix = pd.read_csv(distance_matrix_path, sep=";", index_col=0)
    distance_matrix.index = distance_matrix["Name"]
    distance_matrix.drop(columns=["Name"], inplace=True)
    cost_matrix = distance_to_cost(6.62, 17.5, distance_matrix)
    #print(cost_matrix)
