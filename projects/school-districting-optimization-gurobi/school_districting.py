from gurobipy import GRB, Model, quicksum


students = {
    ("Neighborhood1", "K"): 30,
    ("Neighborhood1", "1"): 25,
    ("Neighborhood2", "K"): 28,
    ("Neighborhood2", "1"): 22,
}

capacities = {
    ("School1", "K"): 40,
    ("School1", "1"): 40,
    ("School2", "K"): 50,
    ("School2", "1"): 50,
}

schools_serving_grades = {
    "School1": ["K", "1"],
    "School2": ["K", "1"],
}

distances = {
    ("Neighborhood1", "School1"): 2.0,
    ("Neighborhood1", "School2"): 3.0,
    ("Neighborhood2", "School1"): 1.5,
    ("Neighborhood2", "School2"): 2.5,
}

neighborhoods = sorted({n for n, _ in students})
schools = sorted(schools_serving_grades)
grades = sorted({g for _, g in students})

feasible_assignments = [
    (n, s, g)
    for n in neighborhoods
    for s in schools
    for g in grades
    if (n, g) in students
    and g in schools_serving_grades[s]
    and (s, g) in capacities
    and (n, s) in distances
]

model = Model("SchoolDistricting")

x = model.addVars(feasible_assignments, vtype=GRB.BINARY, name="assign")

model.setObjective(
    quicksum(
        distances[n, s] * students[n, g] * x[n, s, g]
        for n, s, g in feasible_assignments
    ),
    GRB.MINIMIZE,
)

for s in schools:
    for g in grades:
        if (s, g) in capacities:
            model.addConstr(
                quicksum(
                    students[n, g] * x[n, s, g]
                    for n in neighborhoods
                    if (n, s, g) in x
                )
                <= capacities[s, g],
                name=f"capacity_{s}_{g}",
            )

for n in neighborhoods:
    for g in grades:
        if (n, g) in students:
            model.addConstr(
                quicksum(
                    x[n, s, g]
                    for s in schools
                    if (n, s, g) in x
                )
                == 1,
                name=f"assignment_{n}_{g}",
            )

model.optimize()

if model.Status == GRB.OPTIMAL:
    print(f"Optimal objective value: {model.ObjVal:.2f}")
    print("Assignments:")
    for n, s, g in feasible_assignments:
        if x[n, s, g].X > 0.5:
            print(
                f"  {n}, grade {g} -> {s} "
                f"({students[n, g]} students, distance {distances[n, s]:.2f})"
            )
elif model.Status == GRB.INFEASIBLE:
    print("The model is infeasible.")
    model.computeIIS()
    model.write("school_districting.ilp")
    print("An IIS was written to school_districting.ilp")
else:
    print(f"Optimization ended with status code {model.Status}.")
