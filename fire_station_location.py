"""Fire station location covering optimization using PuLP.

This educational example formulates a capacitated set-covering style facility
location problem for emergency response planning. All names and data are
fictional and are provided solely for demonstration and research purposes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import pulp


@dataclass(frozen=True)
class CityData:
    name: str
    construction_cost: int
    station_capacity: int
    demand: int
    required_coverage: int


CITIES: List[CityData] = [
    CityData("Northfield", 32, 85, 42, 1),
    CityData("Eastport", 27, 70, 38, 1),
    CityData("Riverton", 35, 90, 55, 2),
    CityData("Hillcrest", 30, 75, 41, 1),
    CityData("Lakeside", 29, 80, 48, 2),
    CityData("Westhaven", 31, 78, 44, 1),
    CityData("Brookdale", 26, 68, 36, 1),
    CityData("Southgate", 34, 88, 52, 1),
]

MAX_RESPONSE_TIME = 15
TOTAL_BUDGET = 125

# Symmetric fictional travel-time matrix in minutes.
TRAVEL_TIME = [
    [0, 9, 17, 14, 22, 20, 11, 24],
    [9, 0, 12, 18, 16, 21, 13, 19],
    [17, 12, 0, 10, 8, 15, 20, 14],
    [14, 18, 10, 0, 13, 11, 17, 16],
    [22, 16, 8, 13, 0, 9, 18, 12],
    [20, 21, 15, 11, 9, 0, 14, 10],
    [11, 13, 20, 17, 18, 14, 0, 15],
    [24, 19, 14, 16, 12, 10, 15, 0],
]


def build_coverage_sets() -> Dict[int, List[int]]:
    """Return candidate station locations that can reach each city in time."""
    return {
        i: [j for j in range(len(CITIES)) if TRAVEL_TIME[i][j] <= MAX_RESPONSE_TIME]
        for i in range(len(CITIES))
    }


def solve_model() -> tuple[pulp.LpProblem, Dict[int, pulp.LpVariable]]:
    """Build and solve the mixed-integer optimization model."""
    coverage_sets = build_coverage_sets()

    model = pulp.LpProblem("Fire_Station_Location_Covering", pulp.LpMinimize)

    x = {
        i: pulp.LpVariable(f"station_{i}", lowBound=0, upBound=1, cat="Binary")
        for i in range(len(CITIES))
    }

    # Primary objective: minimize total construction cost.
    model += pulp.lpSum(CITIES[i].construction_cost * x[i] for i in x)

    # Coverage requirements. High-priority cities require two independent stations.
    for i, city in enumerate(CITIES):
        model += (
            pulp.lpSum(x[j] for j in coverage_sets[i]) >= city.required_coverage,
            f"coverage_{i}",
        )

    # Total budget ceiling.
    model += (
        pulp.lpSum(CITIES[i].construction_cost * x[i] for i in x) <= TOTAL_BUDGET,
        "budget_limit",
    )

    # Aggregate capacity requirement: selected stations must support total demand.
    model += (
        pulp.lpSum(CITIES[i].station_capacity * x[i] for i in x)
        >= pulp.lpSum(city.demand for city in CITIES),
        "aggregate_capacity",
    )

    solver = pulp.PULP_CBC_CMD(msg=False)
    model.solve(solver)

    return model, x


def verify_solution(x: Dict[int, pulp.LpVariable]) -> None:
    """Validate coverage and capacity for the chosen solution."""
    coverage_sets = build_coverage_sets()
    chosen = {i for i in x if pulp.value(x[i]) > 0.5}

    for i, city in enumerate(CITIES):
        covered_by = [j for j in coverage_sets[i] if j in chosen]
        if len(covered_by) < city.required_coverage:
            raise RuntimeError(f"Coverage verification failed for {city.name}.")

    total_capacity = sum(CITIES[i].station_capacity for i in chosen)
    total_demand = sum(city.demand for city in CITIES)
    if total_capacity < total_demand:
        raise RuntimeError("Capacity verification failed.")


def print_solution(model: pulp.LpProblem, x: Dict[int, pulp.LpVariable]) -> None:
    """Print an interpretable solution summary."""
    status = pulp.LpStatus[model.status]
    print(f"Solver status: {status}")

    if status != "Optimal":
        return

    verify_solution(x)

    selected = [i for i in x if pulp.value(x[i]) > 0.5]
    total_cost = sum(CITIES[i].construction_cost for i in selected)
    total_capacity = sum(CITIES[i].station_capacity for i in selected)
    total_demand = sum(city.demand for city in CITIES)

    print("\nSelected fire station locations:")
    for i in selected:
        city = CITIES[i]
        print(
            f"- {city.name}: cost={city.construction_cost}, "
            f"capacity={city.station_capacity}"
        )

    print(f"\nTotal construction cost: {total_cost}")
    print(f"Budget limit: {TOTAL_BUDGET}")
    print(f"Total selected capacity: {total_capacity}")
    print(f"Total regional demand: {total_demand}")

    print("\nCoverage verification:")
    coverage_sets = build_coverage_sets()
    selected_set = set(selected)
    for i, city in enumerate(CITIES):
        providers = [CITIES[j].name for j in coverage_sets[i] if j in selected_set]
        print(
            f"- {city.name}: required={city.required_coverage}, "
            f"covered_by={providers}"
        )


if __name__ == "__main__":
    optimization_model, station_variables = solve_model()
    print_solution(optimization_model, station_variables)
