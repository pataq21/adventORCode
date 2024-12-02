## Key Concepts:
- **Nodes (Cities)**: Each city represents a node in the graph.
- **Edges (Connections)**: Each connection between cities has an associated weight:
  - **Distance**: Represents the cost of the path to minimize.
  - **Fuel Cost**: Defines the budget constraint.
- **Budget Constraint**: The total fuel cost of the selected connections cannot exceed €73.

---

## Mathematical Model:

### Variables:
- \( x_{i,j} \): Binary variable, where \( x_{i,j} = 1 \) if the connection between cities \( i \) and \( j \) is used, and \( 0 \) otherwise.

### Objective Function:
Minimize the total distance traveled:
\[
\min \sum_{(i,j)} x_{i,j} \cdot \text{distance}_{i,j}
\]

### Constraints:
1. **Fuel Budget**:
   \[
   \sum_{(i,j)} x_{i,j} \cdot \text{fuel\_cost}_{i,j} \leq 73
   \]
   
2. **Flow from Madrid**:
   \[
   \sum_{j} x_{1,j} = 1 \quad (\text{Exactly one outgoing path from Madrid})
   \]

3. **Flow to Copenhagen**:
   \[
   \sum_{i} x_{i,100} = 1 \quad (\text{Exactly one incoming path to Copenhagen})
   \]

4. **Flow Balance for Intermediate Nodes**:
   \[
   \sum_{i} x_{i,k} = \sum_{j} x_{k,j}, \quad \forall k \in \{2, \dots, 99\}
   \]

---

This problem can be solved using optimization tools such as **ORTools** or any other optimization library.
