from typing import List
from dataclasses import dataclass

@dataclass
class Location:
    idx: int
    name: str

@dataclass
class OilField(Location):
    production: float

@dataclass
class Truck:
    idx: int
    start: Location
    end: Location
    route: List[Location]
    fixed_cost: float
    var_cost: float
    capacity: float

@dataclass
class Solution:
    trucks: List[Truck]
    total_cost: float