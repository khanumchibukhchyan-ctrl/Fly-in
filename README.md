*This project has been created as part of the 42 curriculum by kchibukh.*

# Fly-in

## Description

Fly-in is a Python project that simulates multiple drones travelling through a network of interconnected zones.

The main goal is to transport all drones from a starting hub to an ending hub while respecting movement rules, zone capacities, and connection capacities.

The project implements a map parser, graph representation, pathfinding algorithm, simulation engine, and graphical visualization.

The simulation must coordinate multiple drones, find efficient routes, and prevent invalid movements such as exceeding zone or connection capacities.

## Instructions

### Requirements

- Python 3
- Matplotlib
- Flake8
- Mypy

### Installation

Install the required dependencies:

```bash
python3 -m pip install matplotlib flake8 mypy
```

Alternatively, use the Makefile:

```bash
make install
```

### Execution

Run the simulation with the default map:

```bash
make run
```

Run the simulation with a specific map:

```bash
make run MAP=maps/easy/01_linear_path.txt
```

You can also execute the program directly:

```bash
python3 main.py maps/easy/01_linear_path.txt
```

### Code Quality

Run Flake8 and Mypy:

```bash
make lint
```

Run parser tests:

```bash
python3 test_parser.py
```

## Algorithm Choices and Implementation Strategy

### Graph Representation

The map is represented as an undirected graph.

- Zones represent vertices.
- Connections represent edges.
- Each zone stores its name, coordinates, type, capacity, and color.
- Each connection stores its endpoints and maximum capacity.

The graph structure allows the program to find neighboring zones and calculate possible routes.

### Map Parsing

The parser reads the input map file and creates the graph.

It validates:
- The number of drones.
- Zone definitions and coordinates.
- Unique zone names.
- Starting and ending hubs.
- Connection endpoints.
- Connection duplicates.
- Metadata syntax and capacity values.

Invalid maps are rejected with descriptive error messages.

### Pathfinding

The pathfinding algorithm uses a priority queue and a Dijkstra-style search to find efficient routes.

Movement costs are determined by zone types:

- Normal zones have a movement cost of one turn.
- Restricted zones have a movement cost of two turns.
- Blocked zones cannot be used.
- Priority zones are preferred when routes have equal movement costs.

The algorithm also considers route load information when evaluating possible paths.

### Drone Simulation

The simulation engine manages the movement of all drones.

Each drone stores its identifier, current zone, assigned route, and transit information.

During each simulation turn, the engine:

1. Checks drones that are currently travelling through restricted zones.
2. Plans possible drone movements.
3. Checks destination zone capacity.
4. Checks connection capacity.
5. Prevents movements that would exceed capacity limits.
6. Applies valid movements.
7. Updates drone positions and delivery status.

The simulation continues until all drones reach the ending hub or an error prevents further progress.

## Visual Representation

The project uses Matplotlib to display the map and the simulation.

The graphical representation helps users understand the structure of the map and observe drone movements.

The visualization includes:
- Zones displayed at their map coordinates.
- Connections between zones.
- Different colors for visual distinction between zones.
- Drone positions during the simulation.
- Updates as the simulation progresses.

This makes it easier to follow the movement of multiple drones and understand how they travel through the network.

## Example

### Input

Example map:

```text
nb_drones: 1

start_hub: start 0 0 [color=green]
hub: middle 1 0
end_hub: end 2 0 [color=red]

connection: start-middle
connection: middle-end
```

### Expected Output

The drone travels from the starting hub through the middle zone and reaches the ending hub.

```text
D1-middle
D1-end
```

The simulation finishes when the drone reaches the ending hub.

*Note: This is an illustrative example of the expected movement output. The actual output should be checked against the program.*

## Project Structure

```text
Fly-in/
│
├── main.py
├── Makefile
├── README.md
├── requirements.txt
├── test_map.txt
│
├── maps/
│   ├── easy/
│   ├── medium/
│   ├── hard/
│   └── challenger/
│
├── src/
│   ├── models/
│   │   ├── zone.py
│   │   ├── drone.py
│   │   ├── connection.py
│   │   └── graph.py
│   │
│   ├── parser/
│   │   └── map_parser.py
│   │
│   ├── pathfinding/
│   │   └── pathfinder.py
│   │
│   ├── simulation/
│   │   ├── simulator.py
│   │   └── scheduler.py
│   │
│   └── display/
│       └── renderer.py
│
└── test_parser.py
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

All suggested solutions were reviewed, tested, and adapted during the development process. AI was used as an assistant, while the implementation and verification of the project remained part of the development work.