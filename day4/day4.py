from ortools.math_opt.python import mathopt
import pandas as pd


def read_schedule_requirements(file_path, dimensions):
    schedule = {}
    current_room = 0
    current_class = 0

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            parts = list(map(int, line.split('  ')))
            if current_room not in schedule:
                schedule[current_room] = {}

            if current_class not in schedule[current_room]:
                schedule[current_room][current_class] = {}

            for current_teacher, value in enumerate(parts):
                schedule[current_room][current_class][current_teacher] = value

            current_class += 1
            if current_class == dimensions['NUMBER_OF_CLASSES']:
                current_class = 0
                current_room += 1

    return schedule


def read_instance_note(file_path):
    # Lee las dimensiones del problema
    dimensions = {}
    with open(file_path, 'r') as file:
        for line in file:
            # Ignora las líneas que comienzan con #
            if not line.startswith('#'):
                parts = line.split('=')
                dimensions[parts[0].strip()] = int(parts[1].strip())
    return dimensions


def read_instance_files(instance_req_path, instance_note_path):
    dimensions = read_instance_note(instance_note_path)

    # Leer la instancia de requisitos
    matrix = read_schedule_requirements(instance_req_path, dimensions)

    # Leer las dimensiones del problema

    return matrix, dimensions


def solve_scheduling_problem(matrix, dimensions):
    n_periods = 6*5
    n_teachers = dimensions['NUMBER_OF_TEACHERS']
    n_classes = dimensions['NUMBER_OF_CLASSES']
    n_rooms = dimensions['NUMBER_OF_ROOM_AVAILABLE']

    model = mathopt.Model(name="scheduling")
    x = {
        (teacher, room, i_class, period): model.add_binary_variable(name=f"x_{teacher}_{room}_{i_class}_{period}")
        for period in range(n_periods)
        for teacher in range(n_teachers)
        for i_class in range(n_classes)
        for room in range(n_rooms)
    }
    for teacher in range(n_teachers):
        for i_class in range(n_classes):
            for room in range(n_rooms):
                model.add_linear_constraint(
                    sum(x[(teacher, room, i_class, period)]
                        for period in range(n_periods)) == matrix[room][i_class][teacher],
                    name=f'requirement_{teacher}_{room}_{i_class}'
                )

    for room in range(n_rooms):
        for period in range(n_periods):
            model.add_linear_constraint(
                sum(x[(teacher, room, i_class, period)]
                    for i_class in range(n_classes)
                    for teacher in range(n_teachers)) <= 1,
                name=f'no_overlaping_{room}_{period}'
            )

    for teacher in range(n_teachers):
        for period in range(n_periods):
            model.add_linear_constraint(
                sum(x[(teacher, room, i_class, period)]
                    for room in range(n_rooms)
                    for i_class in range(n_classes)) <= 1,
                name=f'no_double_booking_{teacher}_{period}'
            )
    for i_class in range(n_classes):
        for period in range(n_periods):
            model.add_linear_constraint(
                sum(x[(teacher, room, i_class, period)]
                    for room in range(n_rooms)
                    for teacher in range(n_teachers)) <= 1,
                name=f'no_double_class_{i_class}_{period}'
            )

    model.maximize(
        sum(x[(teacher, room, i_class, period)] for teacher, room, i_class, period in x)
    )
    params = mathopt.SolveParameters(enable_output=True)
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)

    # Supongamos que ya tienes los valores de solución
    solution = []
    for period in range(n_periods):
        for teacher in range(n_teachers):
            for i_class in range(n_classes):
                for room in range(n_rooms):
                    if result.variable_values()[x[teacher, room, i_class, period]] > 0.5:  # Variable activa
                        solution.append({
                            "Day": period // 6,  # 6 periodos por día
                            "Period": period % 6,  # Periodos dentro de un día
                            "Room": int(room),
                            "Teacher": int(teacher),
                            "Class": int(i_class)
                        })

    df = pd.DataFrame(solution)

    # Creamos una columna combinada "teacher - class"
    df["Teacher-Class"] = df["Teacher"].astype(str) + " - " + df["Class"].astype(str)

    # Visualizar en formato tabla por salón con combinación teacher-class
    for room in range(n_rooms):
        room_schedule = df[df["Room"] == room].pivot(index="Period", columns="Day", values="Teacher-Class")
        print(f"\nRoom {room} Schedule:")
        print(room_schedule)


# Especificar las rutas de los archivos
instance_req_path = 'day4/instance_req.txt'
instance_note_path = 'day4/instance_note.txt'

# Llamar a la función principal
matrix, dimensions = read_instance_files(instance_req_path, instance_note_path)
solve_scheduling_problem(matrix, dimensions)
