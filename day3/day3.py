from ortools.math_opt.python import mathopt


def read_task_assignment(file_path):
    """
    Reads a text file containing task assignment costs, ignoring commented lines.

    :param file_path: Path to the text file.
    :return: An integer representing the number of tasks and employees,
             and a matrix with assignment costs.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Filter out commented lines and strip whitespace
    lines = [line.strip() for line in lines if not line.strip().startswith("#") and line.strip()]

    # Get the number of tasks and employees
    n_tasks = int(lines[0])

    # Read the costs into a matrix
    costs = []
    for line in lines[1:]:
        costs.extend(map(int, line.split()))

    # Verify the number of costs matches expectations
    if len(costs) != n_tasks * n_tasks:
        raise ValueError("The file does not contain the expected number of costs.")

    # Transform the flat list into an n_tasks x n_tasks matrix
    cost_matrix = [costs[i * n_tasks:(i + 1) * n_tasks] for i in range(n_tasks)]

    return n_tasks, cost_matrix


def task_assignment(n_tasks, cost_matrix):
    model = mathopt.Model(name="task_assignment")
    x = {
        (task, employee): model.add_binary_variable(name=f"x_{task}_{employee}")
        for task in range(n_tasks)
        for employee in range(n_tasks)
    }
    for employee in range(n_tasks):
        model.add_linear_constraint(
            sum(x[(task, employee)] for task in range(n_tasks)) == 1,
            name=f'employee_constraint_{employee}'
        )

    for task in range(n_tasks):
        model.add_linear_constraint(
            sum(x[(task, employee)] for employee in range(n_tasks)) == 1,
            name=f'task_constraint_{task}'
        )
    model.minimize(
        sum(x[(task, employee)] * cost_matrix[task][employee] for task, employee in x)
    )
    params = mathopt.SolveParameters(enable_output=True)
    solution = mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)

    if solution:
        print(solution)
        assignment = {
            (task, employee): solution.variable_values()[x[task, employee]]
            for (task, employee) in x
        }

        print("Optimal Assignment:")
        for task, employee in assignment:
            if assignment[(task, employee)] > 0.5:
                print(f"Task {task} is assigned to Employee {employee}")

        optimal_cost = sum(
            assignment[(task, employee)] * cost_matrix[task][employee]
            for task in range(n_tasks)
            for employee in range(n_tasks)
        )
        print(f"Optimal Cost: {optimal_cost}")

    else:
        print("No feasible solution found.")


if __name__ == "__main__":
    file_path = 'day3/instance.txt'
    n_tasks, cost_matrix = read_task_assignment(file_path)
    task_assignment(n_tasks, cost_matrix)
