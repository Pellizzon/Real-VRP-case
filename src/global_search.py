import os
import sys
import time
from copy import deepcopy
from dataclasses import dataclass
from datetime import timedelta
from typing import List, Tuple

import numpy as np
import pandas as pd
from termcolor import colored

sys.path.insert(0, "../")

from src.utils import (
    DistanceMatrix,
    Location,
    OilField,
    Solution,
    Truck,
    distance_to_cost,
    format_solution_output,
    liter_to_bbl,
)


@dataclass
class GlobalSolver:
    cost_matrix: pd.DataFrame
    locations_info: pd.DataFrame
    optimal_solution: Solution
    dist_matrix: pd.DataFrame = None

    def __setup_locations(self) -> Tuple[List[OilField], Location]:
        """Separates depot from oil fields and builds its support list.

        Returns:
            Tuple[List[OilField], List[OffloadSite]]: List of OilField objects and Depot location.
        """
        oil_fields = []
        field_count = 0
        for i, name in enumerate(self.locations_info.index):
            if self.locations_info["Depot"][i] == 0:
                oil_fields += [
                    OilField(
                        idx=field_count,
                        name=name,
                        production=self.locations_info["Production"][i],
                    )
                ]
                field_count += 1
            else:
                depot = Location(idx=0, name=name)
        return (oil_fields, depot)

    def __calculate_total_cost(self, trucks: List[Truck]) -> float:
        """Calculates the total cost of a solution.

        Args:
            trucks (List[Truck]): List of trucks.

        Returns:
            float: Total cost of the solution.
        """
        return sum(map(lambda x: x.fixed_cost + x.var_cost if x.route else 0.0, trucks))

    def __setup_trucks(
        self, num_trucks: int, truck_capacity: float, depot: Location
    ) -> List[Truck]:
        """Builds a list of N trucks that will pickup oil at the oil fields and deliver it
        at offload sites.

        Args:
            num_trucks (int): Number of trucks available.
            truck_capacity (float): Total truck capacity (Liters).
            depot (Location): Depot location object.

        Returns:
            List[Truck]: List of Truck objects
        """
        capacity = liter_to_bbl(volume=truck_capacity)
        trucks = []
        for i in range(num_trucks):
            trucks += [
                Truck(
                    idx=i,
                    route=[],
                    fixed_cost=300,
                    var_cost=0,
                    capacity=capacity,
                    start=depot,
                    end=depot,
                )
            ]
        return trucks

    def __solve(
        self,
        visited: List[OilField],
        trucks: List[Truck],
        oil_fields: List[OilField],
        solution: List[Truck],
        optimal_cost: int,
    ) -> Tuple[List[Truck], float]:
        """Algorithm that solves the VRP.

        Args:
            visited (List[OilField]): List of visited oil fields.
            offloaded (List[Truck]): List of trucks that already offloaded their cargo.
            trucks (List[Truck]): List of trucks.
            oil_fields (List[OilField]): List of oil fields.
            solution: (List[Truck]): Object containing list of trucks of the best solution.
            optimal_cost: (float): Cost of best solution.

        Returns:
            Solution: Object containing best routes and total cost.
        """
        if len(visited) == len(oil_fields):
            total_cost = self.__calculate_total_cost(trucks)

            if total_cost < optimal_cost:
                optimal_cost = total_cost
            return trucks, optimal_cost

        for t in trucks:
            for f in oil_fields:
                if f not in visited:
                    if t.capacity - f.production >= 0:
                        visited += [f]
                        if len(t.route) == 0:
                            t.var_cost += self.cost_matrix[t.start.name][f.idx]
                            t.var_cost += self.cost_matrix[f.name][t.end.idx]
                        else:
                            t.var_cost -= self.cost_matrix[t.route[-1].name][t.end.idx]
                            t.var_cost += self.cost_matrix[t.route[-1].name][f.idx]
                            t.var_cost += self.cost_matrix[f.name][t.end.idx]
                        t.route += [f]
                        t.capacity -= f.production
                        ret_trucks, ret_cost = self.__solve(
                            visited=visited,
                            trucks=trucks,
                            oil_fields=oil_fields,
                            solution=solution,
                            optimal_cost=optimal_cost,
                        )
                        visited.pop()
                        if ret_cost < optimal_cost:
                            solution = deepcopy(ret_trucks)
                            optimal_cost = ret_cost
                        if len(t.route) == 1:
                            t.var_cost = 0
                            t.total_cargo = 0
                        else:
                            t.var_cost += self.cost_matrix[t.route[-2].name][t.end.idx]
                            t.var_cost -= self.cost_matrix[t.route[-2].name][f.idx]
                            t.var_cost -= self.cost_matrix[f.name][t.end.idx]
                        t.capacity += f.production
                        t.route.pop()
        return solution, optimal_cost

    def run(self, num_trucks: int, truck_capacity: float) -> None:
        """Runs the solver.

        Args:
            num_trucks (int): Number of available trucks.
            truck_capacity (float): Total cargo capacity of the trucks.
        """
        oil_fields, depot = self.__setup_locations()
        trucks = self.__setup_trucks(
            num_trucks=num_trucks,
            truck_capacity=truck_capacity,
            depot=depot,
        )
        solution, optimal_cost = self.__solve(
            visited=[],
            trucks=trucks,
            oil_fields=oil_fields,
            solution=[],
            optimal_cost=np.inf,
        )
        self.optimal_solution.trucks = deepcopy(solution)
        self.optimal_solution.total_cost = optimal_cost


if __name__ == "__main__":
    current_path = os.path.dirname(os.path.abspath(__file__))
    distance_matrix_path = os.path.join(
        current_path, "..", "data", "distance_matrix.csv"
    )
    locations_path = os.path.join(current_path, "..", "data", "locations_reduced.csv")
    locations = pd.read_csv(locations_path, sep=";", index_col=False, encoding="UTF-8")

    distance_matrix = DistanceMatrix(input_data=locations)
    distance_matrix.calculate()
    cost_matrix = distance_to_cost(
        diesel_price=6.62,
        truck_consumption=17.5,
        dist_matrix=distance_matrix.matrix,
    )

    locations.index = locations["Name"]
    locations.drop(columns=["Name"], inplace=True)

    solver = GlobalSolver(
        cost_matrix=cost_matrix,
        locations_info=locations,
        optimal_solution=Solution(trucks=[], total_cost=np.inf),
    )

    truck_capacity = 10000
    start = time.time()
    solver.run(num_trucks=3, truck_capacity=truck_capacity)
    duration = time.time() - start

    format_solution_output(solver, truck_capacity, duration)
