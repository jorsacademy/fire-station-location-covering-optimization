using Test
using CapacitatedFacilityLocationTabuSearch

@testset "Capacitated Facility Location Tabu Search" begin
    data = generate_instance(n_facilities=10, n_customers=20, seed=1234)

    @test length(data.fixed_costs) == 10
    @test length(data.demands) == 20
    @test size(data.transportation_costs) == (10, 20)

    all_open = trues(10)
    feasible, objective, fixed_cost, assignment_result = evaluate_solution(all_open, data)

    @test feasible
    @test isfinite(objective)
    @test isfinite(fixed_cost)
    @test assignment_result.feasible
    @test all(assignment_result.assignment .>= 1)
    @test all(assignment_result.used_capacity .<= data.capacities .+ 1e-8)

    result = tabu_search(data; max_iterations=25, tabu_tenure=5, verbose=false)

    @test isfinite(result.objective)
    @test result.objective <= objective + 1e-8
    @test all(result.assignment .>= 1)
    @test all(result.used_capacity .<= data.capacities .+ 1e-8)
    @test isapprox(
        result.objective,
        result.fixed_cost + result.transportation_cost;
        atol=1e-8,
    )
end
