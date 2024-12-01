from ortools.sat.python import cp_model
from collections import defaultdict

# ---------------------- FUNCIONES ----------------------


def load_instance(file_path):
    """Carga la instancia desde un archivo y construye el grafo."""
    with open(file_path, "r") as file:
        lines = file.readlines()

    # Parsear número de eventos y conflictos
    num_events, num_conflicts = map(int, lines[0].strip().split())

    # Construir grafo como lista de adyacencia
    graph = defaultdict(list)
    conflicts = []
    for line in lines[1:]:
        if line.startswith("e"):  # Procesar solo líneas con conflictos
            _, x, y = line.strip().split()
            x, y = int(x), int(y)
            graph[x].append(y)
            graph[y].append(x)
            conflicts.append((x, y))

    return num_events, conflicts, graph


def greedy_coloring(graph, num_events):
    """Realiza una heurística de coloración greedy."""
    colors = {}
    for node in range(1, num_events + 1):
        # Obtener colores usados por los vecinos
        neighbor_colors = {colors[neighbor] for neighbor in graph[node] if neighbor in colors}
        # Asignar el primer color disponible
        for color in range(num_events):  # Máximo num_events colores posibles
            if color not in neighbor_colors:
                colors[node] = color
                break

    return max(colors.values()) + 1


# ---------------------- FLUJO PRINCIPAL ----------------------

class MySolverCallback(cp_model.CpSolverSolutionCallback):
    """Clase que maneja el callback para mostrar soluciones intermedias."""

    def __init__(self, num_events, rooms_upper_bound,  x, y):
        super().__init__()
        self.num_events = num_events
        self.rooms_upper_bound = rooms_upper_bound
        self.x = x
        self.y = y

    def on_solution_callback(self):
        """Se ejecuta cuando se encuentra una solución."""
        print("\nSolución encontrada:")
        print("Número de salas utilizadas:", self.ObjectiveValue(), self.BestObjectiveBound())


def solve_with_ortools(num_events, conflicts, rooms_upper_bound):
    model = cp_model.CpModel()

    # Variables de decisión: x[i, r] = 1 si el evento i está en la sala r
    x = {}
    for i in range(1, num_events + 1):
        for r in range(1, rooms_upper_bound + 1):
            x[i, r] = model.NewBoolVar(f'x_{i}_{r}')

    # Variables de uso de sala: y[r] = 1 si la sala r está en uso
    y = {}
    for r in range(1, rooms_upper_bound + 1):
        y[r] = model.NewBoolVar(f'y_{r}')

    # Restricción: cada evento debe asignarse a exactamente una sala
    for i in range(1, num_events + 1):
        model.Add(sum(x[i, r] for r in range(1, rooms_upper_bound + 1)) == 1)

    # Restricción: eventos en conflicto no pueden compartir la misma sala
    for (i, j) in conflicts:
        for r in range(1, rooms_upper_bound + 1):
            model.Add(x[i, r] + x[j, r] <= 1)

    # Relación entre uso de salas y asignación de eventos
    for r in range(1, rooms_upper_bound + 1):
        for i in range(1, num_events + 1):
            model.Add(x[i, r] <= y[r])
    model.Add(sum(y[r] for r in range(1, rooms_upper_bound + 1)) >= 1)

    # Función objetivo: minimizar el número de salas usadas
    model.Minimize(sum(y[r] for r in range(1, rooms_upper_bound + 1)))

    # Crear el callback
    callback = MySolverCallback(num_events, rooms_upper_bound,  x, y)

    # Resolver el modelo con el callback
    solver = cp_model.CpSolver()
    solver.parameters.enumerate_all_solutions = True

    status = solver.solve(model, callback)
    print(solver.status_name(status))

# ---------------------- FLUJO PRINCIPAL ----------------------


if __name__ == "__main__":
    # Ruta al archivo de instancia
    file_path = "day1/instance.txt"

    # 1. Cargar datos
    num_events, conflicts, graph = load_instance(file_path)

    # 2. Obtener el número máximo de salas de la heurística de coloración greedy
    rooms_upper_bound = greedy_coloring(graph, num_events)

    # 3. Resolver el modelo con OR-Tools y el callback para ver soluciones intermedias
    solve_with_ortools(num_events, conflicts, rooms_upper_bound)
