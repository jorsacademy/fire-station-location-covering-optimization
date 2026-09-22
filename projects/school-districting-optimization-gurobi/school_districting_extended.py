from gurobipy import GRB, Model, quicksum


students = {
    ("Neighborhood1", "K"): 30,
    ("Neighborhood1", "1"): 25,
    ("Neighborhood2", "K"): 28,
    ("Neighborhood2", "1"): 22,
    ("Neighborhood3", "K"): 18,
    ("Neighborhood3", "1"): 20,
}

capacities = {
    ("School1", "K"): 55,
    ("School1", "1"): 55,
    ("School2", "K"): 55,
    ("School2", "1"): 55,
    ("School3", "K"): 45,
    ("School3", "1"): 45,
}

schools_serving_grades = {
    "School1": ["K", "1"],
    "School2": ["K", "1"],
    "School3": ["K", "1"],
}

distances = {
    ("Neighborhood1", "School1"): 1.2,
    ("Neighborhood1", "School2"): 2.8,
    ("Neighborhood1", "School3"): 4.0,
    ("Neighborhood2", "School1"): 2.0,
    ("Neighborhood2", "School2"): 1.4,
    ("Neighborhood2", "School3"): 2.6,
    ("Neighborhood3", "School1"): 3.8,
    ("Neighborhood3", "School2"): 2.1,
    ("Neighborhood3", "School3"): 1.0,
}

previous_assignment = {
    ("Neighborhood1", "School1", "K"): 1,
    ("Neighborhood1", "School1", "1"): 1,
    ("Neighborhood2", "School2", "K"): 1,
    ("Neighborhood2", "School2", "1"): 1,
    ("Neighborhood3", "School2", "K"): 1,
    ("Neighborhood3", "School2", "1"): 1,
}

minimum_students_if_grade_used = 15
continuity_penalty = 0.75
school_use_penalty = 8.0

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

model = Model("SchoolDistrictingExtended")

x = model.addVars(feasible_assignments, vtype=GRB.BINARY, name="assign")
y = model.addVars(
    [(s, g) for s in schools for g in grades if (s, g) in capacities],
    vtype=GRB.BINARY,
    name="grade_used",
)
z = model.addVars(schools, vtype=GRB.BINARY, name="school_used")

travel_cost = quicksum(
    distances[n, s] * students[n, g] * x[n, s, g]
    for n, s, g in feasible_assignments
)

continuity_cost = quicksum(
    continuity_penalty
    * students[n, g]
    * (1 - previous_assignment.get((n, s, g), 0))
    * x[n, s, g]
    for n, s, g in feasible_assignments
)

school_use_cost = quicksum(school_use_penalty * z[s] for s in schools)

model.setObjective(
    travel_cost + continuity_cost + school_use_cost,
    GRB.MINIMIZE,
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

for s in schools:
    for g in grades:
        if (s, g) not in capacities:
            continue

        enrollment = quicksum(
            students[n, g] * x[n, s, g]
            for n in neighborhoods
            if (n, s, g) in x
        )

        model.addConstr(
            enrollment <= capacities[s, g] * y[s, g],
            name=f"capacity_{s}_{g}",
        )

        model.addConstr(
            enrollment >= minimum_students_if_grade_used * y[s, g],
            name=f"minimum_enrollment_{s}_{g}",
        )

        model.addConstr(
            y[s, g] <= z[s],
            name=f"grade_implies_school_{s}_{g}",
        )

for s in schools:
    model.addConstr(
        z[s]
        <= quicksum(y[s, g] for g in grades if (s, g) in y),
        name=f"school_used_if_grade_used_{s}",
    )

model.optimize()

if model.Status == GRB.OPTIMAL:
    print(f"Optimal objective value: {model.ObjVal:.2f}")
    print(f"Travel component: {travel_cost.getValue():.2f}")
    print(f"Continuity component: {continuity_cost.getValue():.2f}")
    print(f"School-use component: {school_use_cost.getValue():.2f}")

    print("\nAssignments:")
    for n, s, g in feasible_assignments:
        if x[n, s, g].X > 0.5:
            previous = previous_assignment.get((n, s, g), 0) == 1
            print(
                f"  {n}, grade {g} -> {s} "
                f"({students[n, g]} students, distance {distances[n, s]:.2f}, "
                f"previous_assignment={previous})"
            )

    print("\nUsed schools:")
    for s in schools:
        if z[s].X > 0.5:
            print(f"  {s}")

    print("\nGrade-level enrollments:")
    for s in schools:
        for g in grades:
            if (s, g) in y and y[s, g].X > 0.5:
                enrollment_value = sum(
                    students[n, g] * x[n, s, g].X
                    for n in neighborhoods
                    if (n, s, g) in x
                )
                print(
                    f"  {s}, grade {g}: "
                    f"{enrollment_value:.0f}/{capacities[s, g]} students"
                )

elif model.Status == GRB.INFEASIBLE:
    print("The model is infeasible.")
    model.computeIIS()
    model.write("school_districting_extended.ilp")
    print("An IIS was written to school_districting_extended.ilp")
else:
    print(f"Optimization ended with status code {model.Status}.")
