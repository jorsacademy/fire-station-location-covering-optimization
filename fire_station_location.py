"""Fire station location covering optimization using PuLP.

This educational example formulates a set-covering style facility location
problem for emergency response planning. All names and data are fictional and
provided solely for demonstration, education, and non-commercial research.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import pulp


@dataclass(frozen=True)
class CityData:
    name: str
    construction_cost: int
    required_coverage: int


CITIES: List[CityData] = [
    CityData("Northfield", 32, 1),
    CityData("Eastport", 27, 1),
    CityData("Riverton", 35, 2),
    CityData("Hillcrest", 30, 1),
    CityData("Lakeside", 29, 2),
    CityData("Westhaven", 31, 1),
    CityData("Brookdale", 26, 1),
    CityData("Southgate", 34, 1),
]

MAX_RESPONSE_TIME = 15
TOTAL_BUDGET = 130

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
        i: pulp.LpVariable(f"station_{i}", cat="Binary")
        for i in range(len(CITIES))
    }

    # Minimize total construction cost.
    model += pulp.lpSum(CITIES[i].construction_cost * x[i] for i in x)

    # Every city must receive the required number of independent covering stations.
    for i, city in enumerate(CITIES):
        model += (
            pulp.lpSum(x[j] for j in coverage_sets[i]) >= city.required_coverage,
            f"coverage_{i}",
        )

    # Planning budget ceiling.
    model += (
        pulp.lpSum(CITIES[i].construction_cost * x[i] for i in x) <= TOTAL_BUDGET,
        "budget_limit",
    )

    solver = pulp.PULP_CBC_CMD(msg=False)
    model.solve(solver)

    return model, x


def verify_solution(x: Dict[int, pulp.LpVariable]) -> None:
    """Validate all coverage requirements for the selected locations."""
    coverage_sets = build_coverage_sets()
    selected = {i for i in x if pulp.value(x[i]) > 0.5}

    for i, city in enumerate(CITIES):
        providers = [j for j in coverage_sets[i] if j in selected]
        if len(providers) < city.required_coverage:
            raise RuntimeError(f"Coverage verification failed for {city.name}.")


def print_solution(model: pulp.LpProblem, x: Dict[int, pulp.LpVariable]) -> None:
    """Print an interpretable solution summary."""
    status = pulp.LpStatus[model.status]
    print(f"Solver status: {status}")

    if status != "Optimal":
        return

    verify_solution(x)

    selected = [i for i in x if pulp.value(x[i]) > 0.5]
    total_cost = sum(CITIES[i].construction_cost for i in selected)

    print("\nSelected fire station locations:")
    for i in selected:
        city = CITIES[i]
        print(f"- {city.name}: construction cost={city.construction_cost}")

    print(f"\nTotal construction cost: {total_cost}")
    print(f"Budget limit: {TOTAL_BUDGET}")

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
