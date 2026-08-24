# Fire Station Location Covering Optimization

This repository presents a mixed-integer programming model for selecting fire station locations under response-time, redundancy, budget, and aggregate capacity requirements.

The example is intentionally fictional. All place names, costs, capacities, demands, and travel times were created for educational and research use.

## Problem

A regional planner must decide which candidate cities should receive fire stations. A station can cover a city only if its travel time is no greater than the response-time threshold.

The model includes the following requirements:

- Minimize total station construction cost.
- Ensure every city is covered within the maximum response time.
- Require double coverage for selected high-priority cities.
- Respect a total construction budget.
- Ensure the aggregate capacity of selected stations is sufficient for total regional demand.

The decision variable is binary:

```text
x_j = 1 if a fire station is constructed at candidate location j
      0 otherwise
```

The core covering constraint is:

```text
sum(x_j for j in N_i) >= r_i
```

where `N_i` is the set of candidate stations capable of reaching city `i` within the response-time threshold and `r_i` is the required number of covering stations.

## Data

The project uses eight fictional cities and a symmetric travel-time matrix measured in minutes. Two cities are treated as high-priority locations and therefore require coverage from at least two selected stations.

The data are embedded directly in the Python script so that the model can be reproduced without external files.

## Requirements

- Python 3.10 or newer
- PuLP
- CBC solver, normally bundled with standard PuLP installations

Install the dependency with:

```bash
pip install -r requirements.txt
```

## Run

```bash
python fire_station_location.py
```

The script reports:

- solver status,
- selected fire station locations,
- total construction cost,
- total selected capacity,
- total regional demand,
- coverage verification for every city.

## Model Notes

This model is a set-covering style facility-location formulation with additional side constraints. It is designed as a compact operations research example rather than as a production emergency-services planning system.

The aggregate capacity constraint is intentionally simplified. It verifies that total installed capacity is sufficient for total regional demand, but it does not assign individual demand points to specific fire stations. A more advanced formulation could introduce assignment variables, station-specific workload constraints, scenario-based response times, or stochastic demand.

## License

This project is available for personal, academic, educational, and non-commercial research use only. Commercial use is not permitted without prior written authorization. See `LICENSE.md` for the full terms.
