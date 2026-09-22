# School Districting Optimization with Gurobi

This repository contains a fully synthetic mixed-integer linear programming example for school districting and student assignment.

The model assigns neighborhood-grade groups to schools while minimizing weighted travel distance and respecting school capacity and grade availability.

## Scope

The project is designed for educational use in operations research, optimization, and mathematical programming courses.

All names, entities, schools, neighborhoods, and numerical data in this repository are fictional and created solely for teaching purposes.

## Course Notebook

The main learning resource is:

- `school_districting_course.ipynb`

The notebook follows a complete teaching sequence:

1. problem scenario,
2. mathematical formulation,
3. synthetic data,
4. feasible assignment indexing,
5. baseline MILP implementation,
6. optimization and solution reporting,
7. capacity utilization analysis,
8. continuity-preference extension,
9. comparison of previous and optimized assignments,
10. exercises for further modeling practice.

## Model Structure

The baseline model includes:

- neighborhood-grade student populations,
- school capacities by grade,
- school grade availability,
- neighborhood-to-school travel distances,
- binary assignment decisions,
- capacity constraints,
- exactly-one-school assignment constraints,
- grade eligibility restrictions.

The extended formulation adds a continuity preference that penalizes unnecessary reassignment away from a previous school.

## Requirements

- Python 3.10 or newer
- gurobipy
- A valid Gurobi license
- JupyterLab or Jupyter Notebook for the course notebook

Install dependencies with:

```bash
pip install -r requirements.txt
```

Run the baseline Python model with:

```bash
python school_districting.py
```

Run the extended Python model with:

```bash
python school_districting_extended.py
```

Launch the course notebook with:

```bash
jupyter lab school_districting_course.ipynb
```

## Files

- `school_districting_course.ipynb`: complete course notebook
- `school_districting.py`: baseline optimization model
- `school_districting_extended.py`: extended teaching model
- `requirements.txt`: Python dependency list
- `LICENSE`: non-commercial license terms
- `.gitignore`: standard Python exclusions

## License

This repository is provided for personal, academic, and educational use only. Commercial use is prohibited. See `LICENSE` for the complete terms.
