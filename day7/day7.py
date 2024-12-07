from ortools.math_opt.python import mathopt


# Define the function to parse the file
def read_and_parse_instance(file_path):
    result = {}
    dimensions = {}
    dimension_read = False
    with open(file_path, 'r') as file:
        count = 0
        for line in file:
            line = line.strip()

            if line.startswith('#') or not line:
                continue

            if line and not dimension_read:
                dimension_read = True
                n_products, n_subsets = map(int, line.split())
                dimensions = {"n_products": n_products, "n_subsets": n_subsets}
                continue

            parts = list(map(int, line.split()))

            result[count] = {
                "cost": parts[0],
                "elements": parts[2:]
            }
            count += 1
    return dimensions, result


def solve_subset_problem(dimension, instance):
    model = mathopt.Model(name="subset_problem")
    x = {
        (subset): model.add_binary_variable(name=f"x_{subset}")
        for subset in range(dimension['n_subsets'])
    }
    for product in range(1, dimension['n_products'] + 1):
        product_subsets = [x[(subset)]
                           for subset in range(dimension['n_subsets'])
                           if product in instance[subset]['elements']]
        model.add_linear_constraint(

            sum(product_subsets) == 1,
            name=f'product_present_{product}'
        )
    model.minimize(
        sum(x[(subset)] * instance[subset]['cost'] for subset in x)
    )
    params = mathopt.SolveParameters(enable_output=True)
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
    chosen_subsets = [
        subset for subset in x
        if result.variable_values()[x[subset]] > 0.5
    ]

    for subset in chosen_subsets:
        elements = instance[subset]['elements']
        print(f"Subset {subset} includes elements: {elements}")


instance_path = 'day7/instance.txt'

dimensions, result = read_and_parse_instance(instance_path)
solve_subset_problem(dimensions, result)
