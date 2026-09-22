module CapacitatedFacilityLocationTabuSearch

using Random

export ProblemData,
       AssignmentResult,
       SearchResult,
       generate_instance,
       assign_customers,
       evaluate_solution,
       tabu_search,
       print_solution

struct ProblemData
    fixed_costs::Vector{Float64}
    capacities::Vector{Float64}
    demands::Vector{Float64}
    transportation_costs::Matrix{Float64}
    facility_coordinates::Vector{Tuple{Float64, Float64}}
    customer_coordinates::Vector{Tuple{Float64, Float64}}
end

struct AssignmentResult
    feasible::Bool
    assignment::Vector{Int}
    transportation_cost::Float64
    used_capacity::Vector{Float64}
end

struct SearchResult
    open_facilities::BitVector
    objective::Float64
    fixed_cost::Float64
    transportation_cost::Float64
    assignment::Vector{Int}
    used_capacity::Vector{Float64}
    iterations::Int
end

function validate_problem(data::ProblemData)
    n_facilities = length(data.fixed_costs)
    n_customers = length(data.demands)

    n_facilities > 0 || throw(ArgumentError("At least one facility is required."))
    n_customers > 0 || throw(ArgumentError("At least one customer is required."))
    length(data.capacities) == n_facilities || throw(ArgumentError("capacities has an invalid length."))
    length(data.facility_coordinates) == n_facilities || throw(ArgumentError("facility_coordinates has an invalid length."))
    length(data.customer_coordinates) == n_customers || throw(ArgumentError("customer_coordinates has an invalid length."))
    size(data.transportation_costs) == (n_facilities, n_customers) ||
        throw(ArgumentError("transportation_costs must have size (n_facilities, n_customers)."))

    all(isfinite, data.fixed_costs) || throw(ArgumentError("fixed_costs must be finite."))
    all(isfinite, data.capacities) || throw(ArgumentError("capacities must be finite."))
    all(isfinite, data.demands) || throw(ArgumentError("demands must be finite."))
    all(isfinite, data.transportation_costs) || throw(ArgumentError("transportation_costs must be finite."))

    all(x -> x >= 0.0, data.fixed_costs) || throw(ArgumentError("fixed_costs must be nonnegative."))
    all(x -> x >= 0.0, data.capacities) || throw(ArgumentError("capacities must be nonnegative."))
    all(x -> x >= 0.0, data.demands) || throw(ArgumentError("demands must be nonnegative."))
    all(x -> x >= 0.0, data.transportation_costs) || throw(ArgumentError("transportation_costs must be nonnegative."))

    return nothing
end

"""
    generate_instance(; n_facilities=10, n_customers=20, seed=1234)

Create a reproducible synthetic capacitated facility-location instance.
Transportation costs are Euclidean distances between facility and customer coordinates.
"""
function generate_instance(; n_facilities::Int=10, n_customers::Int=20, seed::Int=1234)
    n_facilities > 0 || throw(ArgumentError("n_facilities must be positive."))
    n_customers > 0 || throw(ArgumentError("n_customers must be positive."))

    rng = MersenneTwister(seed)

    facility_coordinates = [(100.0 * rand(rng), 100.0 * rand(rng)) for _ in 1:n_facilities]
    customer_coordinates = [(100.0 * rand(rng), 100.0 * rand(rng)) for _ in 1:n_customers]

    fixed_costs = [200.0 + 200.0 * rand(rng) for _ in 1:n_facilities]
    capacities = [100.0 + 50.0 * rand(rng) for _ in 1:n_facilities]
    demands = [5.0 + 25.0 * rand(rng) for _ in 1:n_customers]

    transportation_costs = Matrix{Float64}(undef, n_facilities, n_customers)
    for i in 1:n_facilities, j in 1:n_customers
        dx = facility_coordinates[i][1] - customer_coordinates[j][1]
        dy = facility_coordinates[i][2] - customer_coordinates[j][2]
        transportation_costs[i, j] = hypot(dx, dy)
    end

    data = ProblemData(
        fixed_costs,
        capacities,
        demands,
        transportation_costs,
        facility_coordinates,
        customer_coordinates,
    )
    validate_problem(data)
    return data
end

"""
    assign_customers(open_facilities, data)

Greedily assign customers to open facilities. Customers are processed in descending
order of demand and each customer is sent to the feasible open facility with the
smallest transportation cost.

This is a heuristic assignment routine. It does not guarantee the minimum possible
assignment cost for a fixed set of open facilities.
"""
function assign_customers(open_facilities::AbstractVector{Bool}, data::ProblemData)
    validate_problem(data)

    n_facilities = length(data.fixed_costs)
    n_customers = length(data.demands)
    length(open_facilities) == n_facilities ||
        throw(ArgumentError("open_facilities has an invalid length."))

    open_indices = findall(identity, open_facilities)
    isempty(open_indices) &&
        return AssignmentResult(false, zeros(Int, n_customers), Inf, zeros(Float64, n_facilities))

    total_open_capacity = sum(data.capacities[i] for i in open_indices)
    total_demand = sum(data.demands)
    total_open_capacity + 1e-10 >= total_demand ||
        return AssignmentResult(false, zeros(Int, n_customers), Inf, zeros(Float64, n_facilities))

    maximum_open_capacity = maximum(data.capacities[i] for i in open_indices)
    maximum(data.demands) <= maximum_open_capacity + 1e-10 ||
        return AssignmentResult(false, zeros(Int, n_customers), Inf, zeros(Float64, n_facilities))

    remaining_capacity = copy(data.capacities)
    used_capacity = zeros(Float64, n_facilities)
    assignment = zeros(Int, n_customers)
    transportation_cost = 0.0

    customer_order = sortperm(data.demands; rev=true)

    for j in customer_order
        best_facility = 0
        best_cost = Inf

        for i in open_indices
            if remaining_capacity[i] + 1e-10 >= data.demands[j]
                cost = data.transportation_costs[i, j]
                if cost < best_cost
                    best_cost = cost
                    best_facility = i
                end
            end
        end

        if best_facility == 0
            return AssignmentResult(false, zeros(Int, n_customers), Inf, zeros(Float64, n_facilities))
        end

        assignment[j] = best_facility
        remaining_capacity[best_facility] -= data.demands[j]
        used_capacity[best_facility] += data.demands[j]
        transportation_cost += best_cost
    end

    return AssignmentResult(true, assignment, transportation_cost, used_capacity)
end

"""
    evaluate_solution(open_facilities, data)

Return `(feasible, objective, fixed_cost, assignment_result)` for a facility-opening vector.
"""
function evaluate_solution(open_facilities::AbstractVector{Bool}, data::ProblemData)
    assignment_result = assign_customers(open_facilities, data)
    if !assignment_result.feasible
        return false, Inf, Inf, assignment_result
    end

    fixed_cost = sum(data.fixed_costs[i] for i in eachindex(open_facilities) if open_facilities[i])
    objective = fixed_cost + assignment_result.transportation_cost
    return true, objective, fixed_cost, assignment_result
end

"""
    tabu_search(data; max_iterations=100, tabu_tenure=5, verbose=true)

Run a one-flip Tabu Search over facility open/closed decisions.

A move toggles one facility. Recently toggled facilities are tabu for `tabu_tenure`
iterations. A tabu move is allowed when it satisfies the aspiration criterion by
improving the best objective found so far.
"""
function tabu_search(
    data::ProblemData;
    max_iterations::Int=100,
    tabu_tenure::Int=5,
    verbose::Bool=true,
)
    validate_problem(data)
    max_iterations > 0 || throw(ArgumentError("max_iterations must be positive."))
    tabu_tenure >= 0 || throw(ArgumentError("tabu_tenure must be nonnegative."))

    n_facilities = length(data.fixed_costs)
    current_solution = trues(n_facilities)

    feasible, current_objective, current_fixed_cost, current_assignment =
        evaluate_solution(current_solution, data)

    feasible || throw(ArgumentError(
        "The all-open initial solution is infeasible under the greedy assignment heuristic. " *
        "Increase capacities, reduce demands, or use a stronger assignment routine."
    ))

    best_solution = copy(current_solution)
    best_objective = current_objective
    best_fixed_cost = current_fixed_cost
    best_assignment = current_assignment

    tabu_until = zeros(Int, n_facilities)
    completed_iterations = 0

    for iteration in 1:max_iterations
        candidate_solution = nothing
        candidate_objective = Inf
        candidate_fixed_cost = Inf
        candidate_assignment = nothing
        candidate_move = 0

        for facility in 1:n_facilities
            neighbor = copy(current_solution)
            neighbor[facility] = !neighbor[facility]

            feasible_neighbor, objective_neighbor, fixed_cost_neighbor, assignment_neighbor =
                evaluate_solution(neighbor, data)

            feasible_neighbor || continue

            is_tabu = iteration <= tabu_until[facility]
            satisfies_aspiration = objective_neighbor < best_objective - 1e-10
            if is_tabu && !satisfies_aspiration
                continue
            end

            if objective_neighbor < candidate_objective - 1e-10
                candidate_solution = neighbor
                candidate_objective = objective_neighbor
                candidate_fixed_cost = fixed_cost_neighbor
                candidate_assignment = assignment_neighbor
                candidate_move = facility
            end
        end

        if candidate_solution === nothing
            verbose && println("No admissible feasible move at iteration $iteration. Search terminated.")
            break
        end

        current_solution = candidate_solution
        current_objective = candidate_objective
        current_fixed_cost = candidate_fixed_cost
        current_assignment = candidate_assignment
        completed_iterations = iteration

        tabu_until[candidate_move] = iteration + tabu_tenure

        if current_objective < best_objective - 1e-10
            best_solution = copy(current_solution)
            best_objective = current_objective
            best_fixed_cost = current_fixed_cost
            best_assignment = current_assignment
        end

        if verbose
            println(
                "Iteration $iteration: current = $(round(current_objective, digits=2)), " *
                "best = $(round(best_objective, digits=2)), move = facility $candidate_move"
            )
        end
    end

    return SearchResult(
        best_solution,
        best_objective,
        best_fixed_cost,
        best_assignment.transportation_cost,
        best_assignment.assignment,
        best_assignment.used_capacity,
        completed_iterations,
    )
end

function print_solution(result::SearchResult, data::ProblemData)
    println("\nBest solution")
    println("-------------")
    println("Total objective:       ", round(result.objective, digits=2))
    println("Fixed facility cost:   ", round(result.fixed_cost, digits=2))
    println("Transportation cost:   ", round(result.transportation_cost, digits=2))
    println("Iterations completed:  ", result.iterations)

    println("\nFacility status and utilization")
    for i in eachindex(result.open_facilities)
        status = result.open_facilities[i] ? "OPEN" : "CLOSED"
        utilization = data.capacities[i] > 0.0 ? 100.0 * result.used_capacity[i] / data.capacities[i] : 0.0
        println(
            "Facility $i: $status | used = $(round(result.used_capacity[i], digits=2)) / " *
            "$(round(data.capacities[i], digits=2)) | utilization = $(round(utilization, digits=1))%"
        )
    end

    println("\nCustomer assignments")
    for j in eachindex(result.assignment)
        println("Customer $j -> Facility $(result.assignment[j])")
    end

    return nothing
end

end
