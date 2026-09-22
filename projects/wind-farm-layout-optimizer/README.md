# Wind Farm Layout Optimizer

A lightweight Python project for generating wind turbine layouts with a randomized greedy heuristic while considering minimum turbine spacing, multiple wind directions, wind probabilities, turbine power output, and simplified wake losses.

## Features

- Places turbines inside a rectangular wind farm boundary.
- Enforces a configurable minimum separation distance.
- Supports multiple wind directions, probabilities, and wind speeds.
- Uses a simplified 2 MW turbine power curve.
- Estimates wake losses using downwind distance and cross-wind offset.
- Scores candidate turbine positions and selects the highest-performing candidate.
- Supports deterministic runs through `random_seed`.
- Visualizes turbine positions, minimum-distance zones, wind direction, and wakes with Matplotlib.

## Requirements

- Python 3.9+
- Matplotlib

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the included example:

```bash
python wind_farm_optimizer.py
```

Or use the optimizer from another Python file:

```python
from wind_farm_optimizer import WindFarmOptimizer

optimizer = WindFarmOptimizer(
    farm_length=2000,
    farm_width=1500,
    min_distance=300,
    turbine_radius=40,
    n_turbines=15,
    wake_effect_radius=400,
    wind_directions=[0, 45, 90, 135, 180, 225, 270, 315],
    wind_probabilities=[0.2, 0.15, 0.1, 0.05, 0.15, 0.2, 0.1, 0.05],
    wind_speeds=[10, 8, 12, 9, 11, 10, 7, 8],
    random_seed=42,
)

result = optimizer.solve()
print(result["total_power"])

optimizer.plot_layout(show_wake=True, direction_index=0)
```

## How the optimization works

For each turbine, the optimizer samples multiple valid candidate positions. Candidates that violate the minimum-distance constraint are rejected. The remaining candidates are evaluated using expected power production across the configured wind scenarios. The candidate with the highest expected power is selected before moving to the next turbine.

This is a heuristic optimizer rather than an exact mathematical optimization solver. It is intended for experimentation, visualization, and educational use.

## Simplified wake model

A turbine can reduce the output of another turbine when the second turbine lies downstream and inside an expanding wake corridor. The maximum individual wake reduction is 30%, with the reduction decreasing as downstream and lateral distance increase.

The wake model is deliberately simplified and should not be treated as an engineering-grade aerodynamic model.

## Project structure

```text
wind-farm-layout-optimizer/
├── wind_farm_optimizer.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Notes

For higher-fidelity wind farm optimization, the heuristic and wake model could be replaced with methods such as genetic algorithms, particle swarm optimization, nonlinear optimization, or established engineering wake models.
