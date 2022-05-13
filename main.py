import os
import time
import pandas as pd
import numpy as np
from termcolor import colored
from datetime import timedelta
from src.global_search import GlobalSolver
from src.utils.distance_matrix import DistanceMatrix
from src.utils.converter import distance_to_cost, liter_to_bbl
from src.utils.models import Solution

def run_global(
    t_count: int,
    t_capacity: float,
    t_consumption: float,
    diesel_price: float
) -> None:
    current_path = os.path.dirname(os.path.abspath(__file__))
    distance_matrix_path = os.path.join(current_path, "data", "distance_matrix.csv")
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

    solver = GlobalSolver(
        cost_matrix=cost_matrix,
        locations_info=locations,
        optimal_solution=Solution(trucks=[], total_cost=np.inf),
    )

    start = time.time()
    solver.run(num_trucks=t_count, truck_capacity=t_capacity)
    duration = time.time() - start

    # Imprime a resposta para o usuário
    print()
    if solver.optimal_solution.total_cost == np.inf:
        print(colored("Não existe uma solução para o problema com as condições inseridas.", "red"))
    else:
        for i, t in enumerate(solver.optimal_solution.trucks):
            print(colored(f"Caminhão {i + 1}", "green"))
            line = f"Rota: {t.start.name} -> "
            for f in t.route:
                line += f"{f.name} -> "
            line += f"{t.end.name}"
            print(line)
            print(f"Carga Total: {liter_to_bbl(truck_capacity) - t.capacity:.2f} bbl")
            print(f"Custo: R$ {t.var_cost + t.fixed_cost:.2f}")
            print()
        print(colored(f"Custo Total Otimizado: {solver.optimal_solution.total_cost}", "yellow"))
        print(colored(f"Solver Time: {timedelta(seconds=duration)}", "blue"))




if __name__ == "__main__":

    truck_count = int(input("Insert the number of available trucks: "))
    truck_capacity = float(input("Insert the capacity of the available trucks: "))
    truck_consumption = float(input("Insert the diesel consumption (km/l) of the available trucks: "))
    diesel_price = float(input("Insert the current diesel price per liter: "))

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
        run_global()

    elif strategy == "2":
        pass
