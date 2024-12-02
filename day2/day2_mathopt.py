from ortools.math_opt.python import mathopt


def parse_input(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Leer cantidad de ciudades, conexiones y presupuesto
    num_cities, num_connections, budget = map(int, lines[0].split())

    # Leer las conexiones
    connections = []
    for line in lines[1:]:
        city1, city2, distance, fuel_cost = map(int, line.split())
        connections.append((city1, city2, distance, fuel_cost))

    return num_cities, num_connections, budget, connections


def solve_shortest_path_with_budget(file_path):
    # Parsear el archivo de entrada
    num_cities, num_connections, budget, connections = parse_input(file_path)

    # Crear el modelo MathOpt
    model = mathopt.Model(name="shortest_path_with_budget")

    # Crear variables binarias: x[i, j] = 1 si usamos el camino de ciudad i a ciudad j
    x = {}
    for i, (city1, city2, _, _) in enumerate(connections):
        x[(city1, city2)] = model.add_binary_variable(name=f"x_{city1}_{city2}")

    # Agregar restricción de presupuesto
    model.add_linear_constraint(
        sum(x[(city1, city2)] * fuel_cost for (city1, city2, _, fuel_cost) in connections) <= budget,
        name="budget_constraint"
    )

    # Garantizar flujo de entrada y salida:
    # Salida de Madrid (nodo 1)
    model.add_linear_constraint(
        sum(x[(city1, city2)] for (city1, city2, _, _) in connections if city1 == 1) == 1,
        name="exit_madrid"
    )
    # Entrada a Copenhagen (nodo 100)
    model.add_linear_constraint(
        sum(x[(city1, city2)] for (city1, city2, _, _) in connections if city2 == 100) == 1,
        name="enter_copenhagen"
    )

    # Balance de flujo intermedio: cualquier nodo excepto 1 y 100 debe tener el mismo flujo de entrada y salida
    for city in range(2, num_cities):
        model.add_linear_constraint(
            sum(x[(city1, city)] for (city1, city2, _, _) in connections if city2 == city) ==
            sum(x[(city, city2)] for (city1, city2, _, _) in connections if city1 == city),
            name=f"flow_balance_{city}"
        )

    # Minimizar la distancia total recorrida
    model.minimize(
        sum(x[(city1, city2)] * distance for (city1, city2, distance, _) in connections)
    )

    # Resolver el modelo
    params = mathopt.SolveParameters(enable_output=True)
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)

    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        raise RuntimeError(f"Model failed to solve: {result.termination}")

    # Imprimir resultados
    # Calcular y ordenar las conexiones usadas
    used_connections = [
        (city1, city2, distance, fuel_cost)
        for (city1, city2, distance, fuel_cost), var in zip(connections, x.values())
        if result.variable_values()[var] > 0.5
    ]

    # Construir el camino ordenado desde la ciudad 1 hasta la ciudad 100
    path = {}
    for city1, city2, _, _ in used_connections:
        path[city1] = city2

    # Seguir el camino desde la ciudad 1
    ordered_path = []
    current_city = 1
    while current_city != 100:
        ordered_path.append(current_city)
        current_city = path[current_city]
    ordered_path.append(100)

    # Calcular el presupuesto utilizado
    total_fuel_cost = sum(fuel_cost for _, _, _, fuel_cost in used_connections)

    # Imprimir resultados
    print("Objective value (total distance):", result.objective_value())
    print("Total fuel cost used:", total_fuel_cost)
    print("Budget available:", budget)
    print("Ordered path:")
    print(" -> ".join(map(str, ordered_path)))


# Main
if __name__ == "__main__":
    file_path = "day2/instance.txt"  # Cambia este nombre al archivo de entrada real
    solve_shortest_path_with_budget(file_path)