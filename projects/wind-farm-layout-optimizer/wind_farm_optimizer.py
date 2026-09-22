import math
import random

import matplotlib.pyplot as plt
from matplotlib.patches import Circle


class WindFarmOptimizer:
    """
    Heuristic wind-farm layout optimizer.

    Turbines are placed inside a rectangular farm while respecting a minimum
    separation distance. Candidate layouts are scored using a simplified wake
    model across multiple wind directions.
    """

    def __init__(
        self,
        farm_length=2000,
        farm_width=2000,
        min_distance=300,
        turbine_radius=40,
        n_turbines=20,
        wake_effect_radius=400,
        wind_directions=None,
        wind_probabilities=None,
        wind_speeds=None,
        random_seed=None,
    ):
        self.farm_length = float(farm_length)
        self.farm_width = float(farm_width)
        self.min_distance = float(min_distance)
        self.turbine_radius = float(turbine_radius)
        self.n_turbines = int(n_turbines)
        self.wake_effect_radius = float(wake_effect_radius)
        self.random_seed = random_seed

        self._validate_geometry()

        default_directions = [0, 45, 90, 135, 180, 225, 270, 315]
        default_probabilities = [0.125] * 8
        default_speeds = [12.0] * 8

        self.wind_directions = list(
            default_directions if wind_directions is None else wind_directions
        )
        self.wind_probabilities = list(
            default_probabilities
            if wind_probabilities is None
            else wind_probabilities
        )
        self.wind_speeds = list(
            default_speeds if wind_speeds is None else wind_speeds
        )

        self._validate_wind_data()
        self.result = None
        self._rng = random.Random(random_seed)

    def _validate_geometry(self):
        if self.farm_length <= 0 or self.farm_width <= 0:
            raise ValueError("Farm dimensions must be positive.")
        if self.min_distance <= 0:
            raise ValueError("min_distance must be positive.")
        if self.turbine_radius <= 0:
            raise ValueError("turbine_radius must be positive.")
        if self.n_turbines <= 0:
            raise ValueError("n_turbines must be a positive integer.")
        if self.wake_effect_radius <= 0:
            raise ValueError("wake_effect_radius must be positive.")

    def _validate_wind_data(self):
        count = len(self.wind_directions)
        if count == 0:
            raise ValueError("At least one wind direction is required.")
        if len(self.wind_probabilities) != count or len(self.wind_speeds) != count:
            raise ValueError(
                "wind_directions, wind_probabilities and wind_speeds "
                "must have the same length."
            )
        if any(speed < 0 for speed in self.wind_speeds):
            raise ValueError("Wind speeds cannot be negative.")
        if any(prob < 0 for prob in self.wind_probabilities):
            raise ValueError("Wind probabilities cannot be negative.")

        probability_sum = sum(self.wind_probabilities)
        if probability_sum <= 0:
            raise ValueError("Wind probabilities must sum to a positive value.")

        self.wind_probabilities = [
            prob / probability_sum for prob in self.wind_probabilities
        ]
        self.wind_directions = [direction % 360 for direction in self.wind_directions]

    @staticmethod
    def calculate_base_power(wind_speed):
        """Simplified 2 MW turbine power curve, returned in kW."""
        if wind_speed < 3:
            return 0.0
        if wind_speed < 12:
            return 2000.0 * (wind_speed - 3.0) / 9.0
        if wind_speed <= 25:
            return 2000.0
        return 0.0

    def _is_valid_position(self, x, y, positions):
        return all(
            math.hypot(x - px, y - py) >= self.min_distance
            for px, py in positions
        )

    def _wake_reduction(self, upstream, downstream, direction_deg):
        """
        Return a fractional power reduction in [0, 0.3].

        The model checks both downstream distance and cross-wind offset.
        """
        angle = math.radians(direction_deg)
        wind_dx = math.cos(angle)
        wind_dy = math.sin(angle)

        rel_x = downstream[0] - upstream[0]
        rel_y = downstream[1] - upstream[1]

        downwind = rel_x * wind_dx + rel_y * wind_dy
        if downwind <= 0 or downwind >= self.wake_effect_radius:
            return 0.0

        crosswind = abs(rel_x * (-wind_dy) + rel_y * wind_dx)
        wake_half_width = self.turbine_radius + 0.10 * downwind
        if crosswind > wake_half_width:
            return 0.0

        distance_decay = 1.0 - downwind / self.wake_effect_radius
        lateral_decay = 1.0 - crosswind / wake_half_width
        return 0.30 * distance_decay * lateral_decay

    def _calculate_total_power(self, positions):
        total_power = 0.0

        for direction, probability, speed in zip(
            self.wind_directions,
            self.wind_probabilities,
            self.wind_speeds,
        ):
            base_power = self.calculate_base_power(speed)
            direction_power = 0.0

            for turbine_index, turbine_position in enumerate(positions):
                turbine_power = base_power

                for upstream_index, upstream_position in enumerate(positions):
                    if upstream_index == turbine_index:
                        continue

                    reduction = self._wake_reduction(
                        upstream_position,
                        turbine_position,
                        direction,
                    )
                    turbine_power *= 1.0 - reduction

                direction_power += turbine_power

            total_power += probability * direction_power

        return total_power

    def solve(self, candidates_per_turbine=250, max_attempts=5000):
        """Build a layout with a randomized greedy heuristic."""
        if candidates_per_turbine <= 0:
            raise ValueError("candidates_per_turbine must be positive.")
        if max_attempts <= 0:
            raise ValueError("max_attempts must be positive.")

        positions = []

        for turbine_number in range(self.n_turbines):
            candidates = []
            attempts = 0

            while len(candidates) < candidates_per_turbine and attempts < max_attempts:
                attempts += 1
                x = self._rng.uniform(0.0, self.farm_length)
                y = self._rng.uniform(0.0, self.farm_width)

                if self._is_valid_position(x, y, positions):
                    candidates.append((x, y))

            if not candidates:
                raise RuntimeError(
                    f"Could only place {turbine_number} of {self.n_turbines} turbines. "
                    "Increase farm dimensions, reduce min_distance/n_turbines, "
                    "or increase max_attempts."
                )

            best_candidate = max(
                candidates,
                key=lambda candidate: self._calculate_total_power(
                    positions + [candidate]
                ),
            )
            positions.append(best_candidate)

        total_power = self._calculate_total_power(positions)

        self.result = {
            "x": [position[0] for position in positions],
            "y": [position[1] for position in positions],
            "total_power": total_power,
        }
        return self.result

    def plot_layout(self, show_wake=False, direction_index=0):
        if self.result is None:
            raise ValueError("Call solve() before plot_layout().")

        if not 0 <= direction_index < len(self.wind_directions):
            raise IndexError("direction_index is outside the wind direction list.")

        fig, ax = plt.subplots(figsize=(10, 8))

        ax.plot(
            [0, self.farm_length, self.farm_length, 0, 0],
            [0, 0, self.farm_width, self.farm_width, 0],
            "k-",
        )

        direction = self.wind_directions[direction_index]
        angle = math.radians(direction)
        dx = math.cos(angle)
        dy = math.sin(angle)

        for x, y in zip(self.result["x"], self.result["y"]):
            ax.add_patch(Circle((x, y), self.turbine_radius, fill=True, alpha=0.7))
            ax.add_patch(
                Circle((x, y), self.min_distance / 2.0, fill=False, alpha=0.2)
            )

            if show_wake:
                wake_length = self.wake_effect_radius
                end_x = x + wake_length * dx
                end_y = y + wake_length * dy
                wake_half_width = self.turbine_radius + 0.10 * wake_length

                ax.plot([x, end_x], [y, end_y], "--", alpha=0.4)

                perp_dx = -dy
                perp_dy = dx
                ax.plot(
                    [
                        end_x - wake_half_width * perp_dx,
                        end_x + wake_half_width * perp_dx,
                    ],
                    [
                        end_y - wake_half_width * perp_dy,
                        end_y + wake_half_width * perp_dy,
                    ],
                    "-",
                    alpha=0.4,
                )

        if show_wake:
            center_x = self.farm_length / 2.0
            center_y = self.farm_width / 2.0
            arrow_length = min(self.farm_length, self.farm_width) / 5.0

            ax.arrow(
                center_x,
                center_y,
                arrow_length * dx,
                arrow_length * dy,
                head_width=arrow_length / 10.0,
                head_length=arrow_length / 8.0,
            )
            ax.text(
                center_x + 1.2 * arrow_length * dx,
                center_y + 1.2 * arrow_length * dy,
                f"Wind: {direction}°",
                fontsize=12,
            )

        ax.set_xlim(-100, self.farm_length + 100)
        ax.set_ylim(-100, self.farm_width + 100)
        ax.set_xlabel("X coordinate (m)")
        ax.set_ylabel("Y coordinate (m)")
        ax.set_title("Heuristic Wind Farm Layout")
        ax.text(
            0.02,
            0.02,
            f"Expected Power: {self.result['total_power']:.2f} kW",
            transform=ax.transAxes,
            fontsize=12,
            bbox=dict(facecolor="white", alpha=0.7),
        )

        ax.grid(True)
        ax.set_aspect("equal", adjustable="box")
        fig.tight_layout()
        return fig


if __name__ == "__main__":
    farm_params = {
        "farm_length": 2000,
        "farm_width": 1500,
        "min_distance": 300,
        "turbine_radius": 40,
        "n_turbines": 15,
        "wake_effect_radius": 400,
        "wind_directions": [0, 45, 90, 135, 180, 225, 270, 315],
        "wind_probabilities": [0.2, 0.15, 0.1, 0.05, 0.15, 0.2, 0.1, 0.05],
        "wind_speeds": [10, 8, 12, 9, 11, 10, 7, 8],
        "random_seed": 42,
    }

    optimizer = WindFarmOptimizer(**farm_params)
    result = optimizer.solve()

    print(f"Optimized layout expected power: {result['total_power']:.2f} kW")

    optimizer.plot_layout(show_wake=True, direction_index=0)
    plt.show()
