include(joinpath(@__DIR__, "..", "src", "CapacitatedFacilityLocationTabuSearch.jl"))

using .CapacitatedFacilityLocationTabuSearch

function main()
    data = generate_instance(
        n_facilities=10,
        n_customers=20,
        seed=1234,
    )

    println("Running Tabu Search for the Capacitated Facility Location Problem...")

    result = tabu_search(
        data;
        max_iterations=100,
        tabu_tenure=5,
        verbose=true,
    )

    print_solution(result, data)
end

main()
