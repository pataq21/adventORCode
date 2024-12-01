## Descripción General

El objetivo de este trabajo es asignar eventos a un conjunto de salas, de manera que los eventos en conflicto no se asignen a la misma sala. Para abordar este problema, se utilizó una combinación de técnicas de **coloración greedy** para obtener una estimación inicial del número de salas necesarias y un **modelo matemático de optimización** basado en **Pyomo** para resolver el problema de manera exacta.

### 1. **Carga de Datos**

El primer paso consiste en leer y cargar los datos de la instancia desde un archivo de texto. El archivo contiene información sobre los eventos y los conflictos entre ellos. Cada línea describe un conflicto entre dos eventos, lo que se utiliza para construir un grafo donde cada evento es un nodo y los conflictos son aristas entre nodos. Esta estructura de grafo es fundamental para realizar la asignación de eventos a las salas de manera eficiente.

**Datos clave leídos del archivo:**

- Número de eventos.
- Número de conflictos.
- Lista de conflictos (pares de eventos que no pueden compartir la misma sala).

### 2. **Coloración Greedy (Heurística)**

Para obtener una estimación inicial del número de salas necesarias, se aplica una **heurística de coloración greedy**. En este enfoque, cada evento se asigna a un "color" (que representa una sala) de manera que los eventos en conflicto no se asignen al mismo color. El algoritmo avanza de la siguiente manera:

- Se asigna un color al primer evento.
- Para cada evento posterior, se asigna el primer color disponible que no haya sido usado por sus vecinos (eventos en conflicto).

Este enfoque asegura que no se asignen dos eventos en conflicto a la misma sala, pero no garantiza la asignación más eficiente en términos de número de salas. Sin embargo, el número de colores utilizados por esta heurística sirve como una **límite superior** del número de salas necesarias, que posteriormente se utilizará como restricción en el modelo matemático.

**Resultado de la heurística greedy:**

- Se obtiene un número estimado de salas necesario para acomodar todos los eventos, lo que se utiliza como límite superior de salas en el modelo matemático.

### 3. **Modelo Matemático de Optimización**

Con la estimación de salas obtenida de la heurística greedy, se procede a construir un modelo de optimización en **Pyomo**, una herramienta de modelado matemático en Python. Este modelo tiene como objetivo asignar los eventos a las salas de manera que se minimice el número total de salas utilizadas, respetando las restricciones de conflictos entre eventos.

#### Variables de Decisión:

- **`x[i, r]`**: Variable binaria que indica si el evento `i` está asignado a la sala `r`.
- **`y[r]`**: Variable binaria que indica si la sala `r` está en uso.

#### Restricciones:

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

1. **Restricción de conflictos**: Los eventos que están en conflicto no pueden ser asignados a la misma sala.
2. **Uso de salas**: Una sala solo puede estar en uso si al menos un evento está asignado a ella.

### Función Objetivo:

El objetivo es **minimizar el número de salas utilizadas**, es decir, minimizar la suma de las variables `y[r]`, que indican si una sala está en uso o no.

Este modelo matemático es una **programación lineal entera mixta** (MIP) que busca una solución óptima, es decir, la asignación de eventos a salas que minimiza el número total de salas, cumpliendo las restricciones mencionadas.

### 5. **Resolución con HiGHS**

Con el archivo MPS generado, se utiliza el solver **HiGHS** para resolver el modelo de optimización. **HiGHS** es un solver eficiente para problemas de programación lineal y entera, que permite obtener soluciones exactas para problemas complejos.

Los pasos realizados en esta fase incluyen:

1. **Lectura del archivo MPS**: El modelo exportado en formato MPS es leído por HiGHS.
2. **Resolución del problema**: HiGHS resuelve el modelo, aplicando técnicas avanzadas de optimización.
3. **Obtención de la solución**: Una vez resuelto el modelo, se extraen las soluciones para las variables de decisión, que indican la asignación de eventos a salas.

### 6. **Resultados**

Finalmente, los resultados obtenidos con **HiGHS** se presentan de la siguiente manera:

- **Estado del solver**: Informa si el solver ha encontrado una solución factible o si ha terminado con algún error.
- **Valor objetivo**: Muestra el número mínimo de salas utilizadas según la solución óptima.
- **Asignación de eventos a salas**: Imprime las asignaciones específicas de cada evento a las salas, lo que permite verificar cómo se han distribuido los eventos de acuerdo con las restricciones de conflicto.
