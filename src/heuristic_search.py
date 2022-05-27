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
class HeuristicSolver:
    cost_matrix: pd.DataFrame
    locations_info: pd.DataFrame
    dist_matrix: pd.DataFrame
    optimal_solution: Solution

    def __setup_locations(self) -> Tuple[List[OilField], Location]:
        """Separates depot from oil fields and builds its support list.

        Returns:
            Tuple[List[OilField], List[OffloadSite]]: List of OilField objects and Depot location.
        """
        oil_fields = []
        field_count = 0
        print(self.locations_info.index)
        for i, name in enumerate(self.locations_info.index):
            if self.locations_info["Depot"][i] == 0:
                oil_fields += [
                    OilField(
                        idx=field_count,
                        name=self.locations_info["Name"][i],
                        production=self.locations_info["Production"][i],
                    )
                ]    
            else:
                depot = Location(idx=field_count, name=self.locations_info["Name"][i])
            field_count += 1
        return (oil_fields, depot)

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

    def __calculate_total_cost(self, trucks: List[Truck]) -> float:
        """Calculates the total cost of a solution.

        Args:
            trucks (List[Truck]): List of trucks.

        Returns:
            float: Total cost of the solution.
        """
        return sum(map(lambda x: x.fixed_cost + x.var_cost if x.route else 0.0, trucks))

    def __solve(
        self,
        visited: List[OilField],
        trucks: List[Truck],
        oil_fields: List[OilField],
    ) -> List[Truck]:
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
        print(self.dist_matrix)
        print(oil_fields)
        for t in trucks:
            test_capacity = False
            if len(t.route) == 0:
                position = t.start.name
            idx_pos = 1
            while not (test_capacity or len(visited) == len(oil_fields)):
                change = False
                next_position_list = np.array(self.dist_matrix[position].T)
                next_position_list_copy = np.sort(next_position_list)
                next_position = np.where(
                    next_position_list == next_position_list_copy[idx_pos]
                )
                for oil in oil_fields:
                    if oil.idx == next_position[0][0]:
                        if oil not in visited:
                            if t.capacity - oil.production >= 0:
                                t.route += [oil]
                                t.capacity -= oil.production
                                t.var_cost += self.cost_matrix[position][oil.name]

                                visited += [oil]
                                position = oil.name
                                idx_pos = 1
                                change = True

                if not (change):
                    idx_pos += 1

                if idx_pos == len(oil_fields) + 1:
                    test_capacity = True

            print(t.route)

        return trucks, self.__calculate_total_cost(trucks)

    def run(self, num_trucks: int, truck_capacity: float) -> None:
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
        )

        self.optimal_solution.trucks = deepcopy(solution)
        self.optimal_solution.total_cost = optimal_cost


if __name__ == "__main__":
    current_path = os.path.dirname(os.path.abspath(__file__))
    locations_path = os.path.join(current_path, "..", "data", "locations.csv")
    locations = pd.read_csv(locations_path, sep=";", index_col=False, encoding="UTF-8")

    distance_matrix = DistanceMatrix(input_data=locations)
    distance_matrix.calculate()
    cost_matrix = distance_to_cost(
        diesel_price=6.62,
        truck_consumption=17.5,
        dist_matrix=distance_matrix.matrix,
    )

    solver = HeuristicSolver(
        cost_matrix=cost_matrix,
        locations_info=locations,
        dist_matrix=distance_matrix.matrix,
        optimal_solution=Solution(trucks=[], total_cost=np.inf),
    )

    truck_capacity = 10000
    start = time.time()
    solver.run(num_trucks=7, truck_capacity=truck_capacity)
    duration = time.time() - start

    format_solution_output(solver, truck_capacity, duration)
