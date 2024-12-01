## General Description

The objective of this work is to assign events to a set of rooms such that conflicting events are not assigned to the same room. To address this problem, a combination of **greedy coloring** techniques was used to obtain an initial estimate of the number of rooms required, and an **optimization mathematical model** based on **Pyomo** was used to solve the problem exactly.

### 1. **Data Loading**

The first step is to read and load the instance data from a text file. The file contains information about the events and the conflicts between them. Each line describes a conflict between two events, which is used to build a graph where each event is a node and conflicts are edges between nodes. This graph structure is fundamental for efficiently assigning events to rooms.

**Key data read from the file:**

- Number of events.
- Number of conflicts.
- List of conflicts (pairs of events that cannot share the same room).

### 2. **Greedy Coloring (Heuristic)**

To get an initial estimate of the number of rooms needed, a **greedy coloring heuristic** is applied. In this approach, each event is assigned a "color" (representing a room) such that conflicting events are not assigned the same color. The algorithm proceeds as follows:

- The first event is assigned a color.
- For each subsequent event, the first available color not used by its neighbors (conflicting events) is assigned.

This approach ensures that no two conflicting events are assigned to the same room but does not guarantee the most efficient room assignment in terms of the number of rooms. However, the number of colors used by this heuristic serves as an **upper bound** for the number of rooms needed, which will later be used as a constraint in the mathematical model.

**Result of the greedy heuristic:**

- An estimated number of rooms required to accommodate all events is obtained, which is used as an upper bound on the number of rooms in the mathematical model.

### 3. **Mathematical Optimization Model**

With the room estimate obtained from the greedy heuristic, we proceed to construct an optimization model in **Pyomo**, a mathematical modeling tool in Python. This model aims to assign events to rooms in such a way that the total number of rooms used is minimized, respecting the conflict constraints between events.

#### Decision Variables:

- **`x[i, r]`**: A binary variable that indicates whether event `i` is assigned to room `r`.
- **`y[r]`**: A binary variable that indicates whether room `r` is in use.

#### Constraints:

$$
\begin{align*}
\text{Minimize} \quad & \sum_{r \in R} y_{r} \\
\text{Subject to:} \quad & \\
& \sum_{r \in R} x_{i,r} = 1 \quad \forall i \in E \\
& x_{i,r} + x_{j,r} \leq 1 \quad \forall (i,j) \in C, \quad \forall r \in R \\
& x_{i,r} \leq y_{r} \quad \forall r \in R, \forall i \in E \\
& x_{i,r} \in \{0,1\} \quad \forall i \in E, \quad \forall r \in R \\
& y_{r} \in \{0,1\} \quad \forall r \in R
\end{align*}
$$

1. **Conflict Constraint**: Events that are in conflict cannot be assigned to the same room.
2. **Room Usage**: A room can only be in use if at least one event is assigned to it.

### Objective Function:

The objective is to **minimize the number of rooms used**, that is, minimize the sum of the variables `y[r]`, which indicate whether a room is in use or not.

This mathematical model is a **Mixed-Integer Linear Programming (MILP)** problem that seeks an optimal solution, i.e., the assignment of events to rooms that minimizes the total number of rooms while satisfying the constraints mentioned above.

### 5. **Solving with CP-SAT**

After several proposals, CP-SAT has shown the best results. I limited the number of variables by obtaining an upper bound on the number of rooms needed. 15 rooms is the best result I could get.
