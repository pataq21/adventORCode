from collections import defaultdict
from pyomo.environ import *
from highspy import Highs

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


def build_optimization_model(num_events, conflicts, rooms_upper_bound):
    """Construye el modelo de optimización en Pyomo."""
    model = ConcreteModel()

    # Conjunto de eventos
    model.events = RangeSet(1, num_events)

    # Conjunto de conflictos (pares de eventos)
    model.conflicts = Set(initialize=conflicts, dimen=2)

    # Número máximo de salas posibles
    max_rooms = rooms_upper_bound

    # Conjunto de salas
    model.rooms = RangeSet(1, max_rooms)

    # Variables de decisión
    model.x = Var(model.events, model.rooms, domain=Binary)  # x[i, r] = 1 si el evento i está en la sala r
    model.y = Var(model.rooms, domain=Binary)  # y[r] = 1 si la sala r es utilizada

    # Restricción: cada evento debe asignarse a exactamente una sala
    def one_room_per_event_rule(model, i):
        return sum(model.x[i, r] for r in model.rooms) == 1
    model.one_room_per_event = Constraint(model.events, rule=one_room_per_event_rule)

    # Restricción: eventos en conflicto no pueden compartir la misma sala
    def no_conflicts_rule(model, i, j, r):
        if (i, j) in model.conflicts or (j, i) in model.conflicts:
            return model.x[i, r] + model.x[j, r] <= 1
        return Constraint.Skip
    model.no_conflicts = Constraint(model.events, model.events, model.rooms, rule=no_conflicts_rule)

    # Relación entre uso de salas y asignación de eventos
    def room_usage_rule(model, i, r):
        return model.x[i, r] <= model.y[r]
    model.room_usage = Constraint(model.events, model.rooms, rule=room_usage_rule)

    # Función objetivo: minimizar el número de salas usadas
    def objective_rule(model):
        return sum(model.y[r] for r in model.rooms)
    model.objective = Objective(rule=objective_rule, sense=minimize)

    return model


def export_model_to_mps(model, mps_path):
    """Exporta el modelo Pyomo a formato MPS."""
    model.write(mps_path, format="mps")


def solve_with_highspy(mps_path):
    """Resuelve el modelo exportado en MPS utilizando HighsPy."""
    highs = Highs()
    highs.readModel(mps_path)
    highs.run()
    return highs


def print_results_highspy(highs):
    """Imprime los resultados obtenidos con HighsPy."""
    solution = highs.getSolution()
    print("\nResultados obtenidos con HighsPy:")
    print("Estado del solver:", highs.getModelStatus())
    print("Valor objetivo:", highs.getObjectiveValue())

    # Extraer variables
    print("\nVariables:")
    for i, value in enumerate(solution.col_value):
        print(f"x[{i}] = {value:.2f}")


# ---------------------- FLUJO PRINCIPAL ----------------------

if __name__ == "__main__":
    # Ruta al archivo de instancia
    file_path = "day1/instance.txt"
    mps_path = "model.mps"

    # 1. Cargar datos
    num_events, conflicts, graph = load_instance(file_path)

    rooms_upper_bound = greedy_coloring(graph, num_events)

    # 2. Construir modelo de optimización en Pyomo
    model = build_optimization_model(num_events, conflicts, rooms_upper_bound)

    # 3. Exportar el modelo a MPS
    export_model_to_mps(model, mps_path)
    print(f"Modelo exportado a {mps_path}")

    # 4. Resolver el modelo utilizando HighsPy
    highs = solve_with_highspy(mps_path)

    # 5. Imprimir resultados de HighsPy
    print_results_highspy(highs)
