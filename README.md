*This project has been created as part of the 42 curriculum by kchibukh.*

# Fly-in

## Description

Fly-in is a Python project that simulates multiple drones travelling through a network of interconnected zones.

The main objective is to transport all drones from a starting hub to an ending hub while respecting movement rules, zone capacities, and connection capacities.

The project implements:

- Map parsing and validation.
- Graph representation.
- Dijkstra-based pathfinding.
- Multi-drone simulation.
- Capacity management.
- Graphical visualization using Matplotlib.

The simulation coordinates multiple drones, calculates routes, and prevents movements that exceed capacity limits.

## Instructions

### Requirements

- Python 3
- Matplotlib
- Flake8
- Mypy

### Installation

Clone or download the project and navigate to its root directory.

Install the dependencies using:

```bash
python3 -m pip install matplotlib flake8 mypy
```

Alternatively, use the Makefile:

```bash
make install
```

### Execution

Run the simulation with a specific map:

```bash
python3 main.py maps/easy/01_linear_path.txt
```

You can also use the Makefile:

```bash
make run MAP=maps/easy/01_linear_path.txt
```

Other available maps are located in:

- `maps/easy/`
- `maps/medium/`
- `maps/hard/`
- `maps/challenger/`

To run a different map, replace the map path in the command.

### Debugging

Run the program using Python's debugger:

```bash
make debug MAP=maps/easy/01_linear_path.txt
```

### Code Quality

Run Flake8 and Mypy:

```bash
make lint
```

For stricter type checking:

```bash
make lint-strict
```

Clean Python cache files:

```bash
make clean
```

## Map Format

Each map describes the number of drones, zones, and connections.

### Number of Drones

The first non-empty, non-comment line must define the number of drones:

```text
nb_drones: 4
```

The number must be a positive integer.

### Zone Definitions

There are three types of zone definitions:

```text
start_hub: start 0 0
hub: middle 1 0
end_hub: goal 2 0
```

Each zone has:
- A unique name.
- X and Y coordinates.
- A zone role.
- Optional metadata.

The map must contain exactly one starting hub and one ending hub.

Start and end hubs do not have capacity limits.

### Zone Metadata

Zones support the following metadata:

- `zone`: Defines the movement type.
- `max_drones`: Defines the maximum number of drones allowed in a zone.
- `color`: Defines the visualization color.

Example:

```text
hub: middle 1 0 [zone=restricted max_drones=2 color=blue]
```

Supported zone types:

| Zone type | Description |
|---|---|
| `normal` | Standard movement, 1 turn |
| `restricted` | Slower movement, 2 turns |
| `priority` | Preferred when movement costs are equal |
| `blocked` | Cannot be used |

Zone capacity is specified using a positive `max_drones` value.

Start and end hubs do not have capacities. Blocked zones cannot have `max_drones`.

### Connections

Connections define which zones are connected.

Example:

```text
connection: start-middle
connection: middle-goal
```

Connections are undirected.

By default, a connection has a capacity of one drone.

Connection capacity can be changed using `max_link_capacity`:

```text
connection: start-middle [max_link_capacity=3]
```

Connection capacities must be positive integers.

### Complete Map Example

```text
nb_drones: 2

start_hub: start 0 0 [color=green]
hub: middle 1 0 [max_drones=2 color=blue]
end_hub: goal 2 0 [color=red]

connection: start-middle [max_link_capacity=2]
connection: middle-goal [max_link_capacity=2]
```

## Algorithm Choices and Implementation Strategy

### Graph Representation

The map is represented as an undirected graph.

- Zones represent vertices.
- Connections represent edges.
- Each zone stores its name, coordinates, role, movement type, capacity, and color.
- Each connection stores its endpoints and maximum capacity.

The graph maintains an adjacency list to efficiently retrieve neighboring zones.

### Map Parsing

The parser reads the input map file and constructs the graph.

It validates:

- The number of drones.
- Zone definitions and coordinates.
- Unique zone names.
- Unique zone coordinates.
- Starting and ending hubs.
- Connection endpoints.
- Duplicate connections, including reversed duplicates.
- Metadata syntax and values.
- Zone and connection capacities.

Invalid maps are rejected with descriptive error messages containing line numbers where applicable.

### Pathfinding

The pathfinding algorithm uses a priority queue and a Dijkstra-style search to find efficient routes.

Movement costs depend on zone types:

- Normal zones have a movement cost of one.
- Restricted zones have a movement cost of two.
- Blocked zones are excluded from possible routes.
- Priority zones receive preference when route costs are equal.

The algorithm also considers zone and connection load information when evaluating possible routes.

### Drone Simulation

The simulation engine manages all drones and coordinates their movements.

Each drone stores:

- Its identifier.
- Its current zone.
- Its assigned path.
- Its current path position.
- Its transit status.

During each simulation turn, the engine:

1. Initializes drones and assigns paths.
2. Checks drones currently travelling through restricted zones.
3. Plans possible movements.
4. Checks destination zone capacity.
5. Checks connection capacity.
6. Prevents movements that would exceed capacity limits.
7. Applies valid movements.
8. Updates drone positions and delivery status.

The simulation continues until all drones reach the ending hub or an error prevents further progress.

### Capacity Management

The simulation respects two types of capacity constraints:

**Zone capacity (`max_drones`)**

Limits the number of drones occupying a zone simultaneously.

**Connection capacity (`max_link_capacity`)**

Limits the number of drones travelling through a connection simultaneously.

Starting and ending hubs have unlimited capacity.

### Restricted Zones

Restricted zones require two turns to traverse.

During the first turn, a drone enters transit. During the following turn, it arrives at its destination.

This behavior is handled by the simulation engine.

## Visual Representation

The project uses Matplotlib to display the map and the simulation.

The graphical representation includes:

- Zones displayed at their map coordinates.
- Connections between zones.
- Connection capacity labels.
- Zone capacity labels.
- Different colors for visual distinction between zones.
- Drone positions during simulation.
- Simulation turn information.
- Visualization updates as drones move.

Drones travelling through restricted connections are displayed between their current and destination zones.

The visualization helps users understand the map structure and observe how multiple drones travel through the network.

## Maps and Challenges

The project includes a collection of maps designed to test different aspects of pathfinding and simulation.

| Category | Maps | Main objective |
|---|---:|---|
| Easy | 3 | Basic navigation and capacity |
| Medium | 3 | Dead ends, loops and priorities |
| Hard | 3 | Complex topology and capacity constraints |
| Challenger | 1 | Advanced optimization and stress testing |

For more information about the maps and their challenges, see:

`maps/README.md`

Recommended testing order:

1. Easy maps: Verify basic functionality.
2. Medium maps: Test pathfinding and capacity management.
3. Hard maps: Test complex routes and coordination.
4. Challenger map: Explore algorithmic optimization.

## Example

### Input

```text
nb_drones: 1

start_hub: start 0 0 [color=green]
hub: middle 1 0
end_hub: goal 2 0 [color=red]

connection: start-middle
connection: middle-goal
```

### Expected Output

```text
D1-middle
D1-goal
```

The simulation finishes when the drone reaches the ending hub.

## Project Structure

```text
Fly-in/
│
├── main.py
├── Makefile
├── README.md
│
├── maps/
│   ├── README.md
│   │
│   ├── easy/
│   │   ├── 01_linear_path.txt
│   │   ├── 02_simple_fork.txt
│   │   └── 03_basic_capacity.txt
│   │
│   ├── medium/
│   │   ├── 01_dead_end_trap.txt
│   │   ├── 02_circular_loop.txt
│   │   └── 03_priority_puzzle.txt
│   │
│   ├── hard/
│   │   ├── 01_maze_nightmare.txt
│   │   ├── 02_capacity_hell.txt
│   │   └── 03_ultimate_challenge.txt
│   │
│   └── challenger/
│       └── 01_the_impossible_dream.txt
│
└── src/
    ├── __init__.py
    │
    ├── models/
    │   ├── __init__.py
    │   ├── zone.py
    │   ├── drone.py
    │   ├── connection.py
    │   └── graph.py
    │
    ├── parser/
    │   └── map_parser.py
    │
    ├── pathfinding/
    │   └── pathfinder.py
    │
    ├── simulation/
    │   └── simulator.py
    │
    └── display/
        └── renderer.py
```

## Resources

### Documentation

- [Python Documentation](https://docs.python.org/3/)
- [Matplotlib Documentation](https://matplotlib.org/stable/)
- [Python Heap Queue Documentation](https://docs.python.org/3/library/heapq.html)
- [Dijkstra's Algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [Mypy Documentation](https://mypy.readthedocs.io/)

### AI Usage

AI tools were used as learning and development assistance during this project.

They helped with:

- Understanding Python concepts and object-oriented programming.
- Explaining algorithms and pathfinding strategies.
- Debugging errors and improving code quality.
- Reviewing simulation logic and capacity management.
- Understanding type hints and static type checking.
- Improving project documentation.

All suggested solutions were reviewed, tested, and adapted during development. AI was used as an assistant, while the implementation and verification of the project remained part of the development work.

---