import os
import time
from ast import Global
from functools import partial
from typing import Union

import numpy as np
import pandas as pd
from termcolor import colored

from src.global_search import GlobalSolver
from src.heuristic_search import HeuristicSolver
from src.utils import (
    DistanceMatrix,
    Solution,
    distance_to_cost,
    format_solution_output,
    liter_to_bbl,
)


def run(
    t_count: int,
    t_capacity: float,
    t_consumption: float,
    diesel_price: float,
    solver: Union[GlobalSolver, HeuristicSolver],
) -> None:
    current_path = os.path.dirname(os.path.abspath(__file__))
    locations_path = os.path.join(current_path, "data", "locations_reduced.csv")
    locations = pd.read_csv(locations_path, sep=";", index_col=False, encoding="UTF-8")

    distance_matrix = DistanceMatrix(input_data=locations)
    distance_matrix.calculate()
    cost_matrix = distance_to_cost(
        diesel_price=diesel_price,
        truck_consumption=t_consumption,
        dist_matrix=distance_matrix.matrix,
    )

    locations.index = locations["Name"]
    locations.drop(columns=["Name"], inplace=True)

    solver = solver(
        cost_matrix=cost_matrix,
        locations_info=locations,
        optimal_solution=Solution(trucks=[], total_cost=np.inf),
        dist_matrix=distance_matrix.matrix,
    )

    start = time.time()
    solver.run(num_trucks=t_count, truck_capacity=t_capacity)
    duration = time.time() - start

    format_solution_output(solver, t_capacity, duration)


if __name__ == "__main__":

    truck_count = int(input("Insert the number of available trucks: "))
    truck_capacity = float(input("Insert the capacity of the available trucks: "))
    truck_consumption = float(
        input("Insert the diesel consumption (km/l) of the available trucks: ")
    )
    diesel_price = float(input("Insert the current diesel price per liter: "))

    configured_run = partial(
        run, truck_count, truck_capacity, truck_consumption, diesel_price
    )

    print(colored("VRP Solver Strategies:", "blue"))
    print()
    print("1 - Global Search")
    print("2 - Heuristic Search")
    print("0 - Quit")
    print()
    strategy = input("Insert the number of the desired solver: ")

    if strategy == "0":
        pass

    elif strategy == "1":
        configured_run(GlobalSolver)

    elif strategy == "2":
        configured_run(HeuristicSolver)
