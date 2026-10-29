# Fly-in

*This project has been created as part of the 42 curriculum by kchibukh*

## Description

**Fly-in** is a Python 3.10+ project that simulates a fleet of drones travelling through a network of connected zones.

The goal of the project is to move all drones from a designated **start zone** to a designated **end zone** in the **fewest possible simulation turns**, while respecting the constraints of the map.

The map is represented as a graph:

* **Zones** are the vertices of the graph.
* **Connections** are the edges between zones.
* **Drones** travel through the connections from the start zone to the end zone.
* Multiple drones may move simultaneously when the capacity rules allow it.

The simulation must take into account:

* Different movement costs.
* Zone capacities.
* Connection capacities.
* Restricted zones.
* Blocked zones.
* Priority zones.
* Multiple drones using the same network.
* Conflicts between drones.
* Strategic waiting.
* Deadlock avoidance.
* Efficient path selection.

The project includes a custom map parser, an object-oriented graph representation, pathfinding, a simulation engine, scheduling logic, and a visual terminal representation.

---

## Features

The project provides:

* Custom map parsing.
* Validation of input maps.
* Object-oriented graph representation.
* Multiple drone simulation.
* Pathfinding without external graph libraries.
* Support for normal, blocked, restricted, and priority zones.
* Zone capacity management.
* Connection capacity management.
* Simultaneous drone movement.
* Restricted movement requiring two turns.
* Collision and conflict prevention.
* Deadlock avoidance.
* Turn-by-turn simulation output.
* Colored terminal visualization.
* Error handling for invalid or unsolvable maps.
* Type checking with `mypy`.
* Code quality checking with `flake8`.

---

## Requirements

The project requires:

* Python 3.10 or newer.
* `pip`.
* `flake8`.
* `mypy`.

A virtual environment is recommended.

You can create one with:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Then install the required dependencies:

```bash
pip install -r requirements.txt
```

---

## Installation

Clone the repository and enter the project directory:

```bash
git clone <repository-url>
cd fly-in-drones
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

---

## Project Structure

A possible project organization is:

```text
fly-in-drones/
├── main.py
├── Makefile
├── README.md
├── .gitignore
├── requirements.txt
│
├── src/
│   ├── __init__.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── zone.py
│   │   ├── connection.py
│   │   ├── drone.py
│   │   └── graph.py
│   │
│   ├── parser/
│   │   ├── __init__.py
│   │   └── map_parser.py
│   │
│   ├── pathfinding/
│   │   ├── __init__.py
│   │   └── pathfinder.py
│   │
│   ├── simulation/
│   │   ├── __init__.py
│   │   ├── simulator.py
│   │   └── scheduler.py
│   │
│   └── display/
│       ├── __init__.py
│       └── renderer.py
│
├── maps/
│   ├── easy/
│   ├── medium/
│   └── hard/
│
└── tests/
    ├── test_parser.py
    ├── test_graph.py
    ├── test_pathfinding.py
    └── test_simulation.py
```

The exact organization may vary, but the project must remain completely object-oriented and type-safe.

---

# Instructions

## Running the Project

The project can be executed using the provided `Makefile`.

### Install dependencies

```bash
make install
```

### Run the simulation

```bash
make run
```

### Run in debug mode

```bash
make debug
```

### Clean generated files

```bash
make clean
```

### Run linting and type checking

```bash
make lint
```

The lint command performs both `flake8` and `mypy` checks.

---

# Input Map Format

The simulation receives a map describing the drone network.

A map contains:

* The number of drones.
* One start zone.
* One end zone.
* Zero or more intermediate zones.
* Connections between zones.
* Optional metadata.

A basic map looks like:

```text
nb_drones: 3

start_hub: start 0 0
end_hub: end 10 10

hub: A 2 2
hub: B 5 5
hub: C 7 7

connection: start-A
connection: A-B
connection: B-C
connection: C-end
```

Comments can be added using `#`:

```text
# Main route
connection: A-B
```

---

## Drones

The first line defines the number of drones:

```text
nb_drones: 5
```

The value must be a positive integer.

Each drone starts at the start zone and must eventually reach the end zone.

The start and end zones are special:

* There must be exactly one start zone.
* There must be exactly one end zone.
* Their capacities are unlimited.
* `max_drones` metadata on these zones is ignored.

---

# Zones

A zone is defined using:

```text
hub: <name> <x> <y>
```

For example:

```text
hub: A 10 20
```

A zone may also contain metadata:

```text
hub: A 10 20 zone=restricted
```

Zone names:

* Must be unique.
* Cannot contain spaces.
* Cannot contain `-`.
* Coordinates must be valid integers.

---

# Zone Types

The project supports four zone types.

## Normal

Normal zones require **1 turn** to enter.

Example:

```text
hub: A 10 20 zone=normal
```

This is also the default if no zone type is specified.

---

## Restricted

Restricted movement requires **2 turns**.

Example:

```text
hub: tunnel 20 30 zone=restricted
```

When a drone enters a restricted connection, it cannot arrive at the destination during the same turn.

It must arrive on the next turn.

A drone also cannot wait extra turns while travelling through a restricted connection.

For example:

```text
A -- B
```

If the movement toward `B` is restricted:

```text
Turn 1: drone enters the connection
Turn 2: drone arrives at B
```

A restricted movement therefore consumes **2 simulation turns**.

---

## Blocked

A blocked zone cannot be used.

Example:

```text
hub: blocked_zone 30 40 zone=blocked
```

Pathfinding must not route drones through blocked zones.

---

## Priority

Priority zones require 1 turn but should be preferred by the pathfinding algorithm when appropriate.

Example:

```text
hub: fast_lane 30 40 zone=priority
```

The algorithm should take the priority property into account when selecting paths.

---

# Zone Capacity

Zones have a maximum number of drones that can occupy them simultaneously.

The default capacity is:

```text
max_drones=1
```

For example:

```text
hub: A 10 20 max_drones=3
```

allows up to three drones to occupy the zone at the same time.

The simulation must never exceed the capacity of a zone.

Two drones cannot enter the same zone during the same turn if doing so would exceed its capacity.

The start and end zones have unlimited capacity.

---

# Connections

Connections are defined using:

```text
connection: <zone1>-<zone2>
```

For example:

```text
connection: A-B
```

Connections are bidirectional.

Therefore:

```text
connection: A-B
```

allows movement:

```text
A -> B
```

and:

```text
B -> A
```

A connection may contain metadata.

For example:

```text
connection: A-B max_link_capacity=2
```

---

# Connection Capacity

Connections have a maximum number of drones that may use them simultaneously.

The default capacity is:

```text
max_link_capacity=1
```

For example:

```text
connection: A-B max_link_capacity=3
```

allows up to three drones to traverse the connection at the same time.

The simulation must respect this capacity.

---

# Colors

Zones may optionally define a color:

```text
hub: A 10 20 zone=normal color=red
```

The color can be used by the visual representation of the simulation.

Any single-word color value may be accepted.

The implementation should provide visual feedback when colors are specified.

---

# Simulation Turns

A **turn** is one discrete step of the simulation.

A turn is **not** the same thing as a graph vertex.

For example, if the path is:

```text
START -> A -> B -> END
```

there are three graph movements:

```text
START -> A
A -> B
B -> END
```

If all movements are normal, the drone needs three turns.

However, if one movement is restricted:

```text
START -> A -> B(restricted) -> END
```

the restricted movement requires two turns.

Therefore, the total number of turns can be greater than the number of graph edges.

---

# Simultaneous Movement

All drone movements during a turn are decided from the state at the **beginning of that turn**.

Drones can move simultaneously if all capacity constraints are respected.

For example:

```text
D1: A -> B
D2: C -> D
```

can happen during the same turn if both movements are valid.

Movement leaving a zone frees capacity during that turn.

Similarly, when a drone arrives at its destination, the appropriate capacity becomes available according to the simulation rules.

---

# Restricted Movement

Restricted movement has special behavior.

When a drone begins a restricted movement:

```text
A -> B
```

the drone is considered to be travelling through the connection.

The first turn represents the beginning of the movement.

The drone reaches `B` on the next turn.

During this period, it cannot wait or change its destination.

The connection remains occupied according to its capacity rules until the drone arrives.

---

# Pathfinding

The project must calculate efficient routes through the graph.

The pathfinding algorithm must consider:

* Distance/path length.
* Zone movement costs.
* Restricted zones.
* Blocked zones.
* Priority zones.
* Graph structure.
* Capacity constraints where relevant.
* Multiple possible paths.

The project must **not** use graph libraries such as:

```text
networkx
graphlib
```

The graph and pathfinding logic must be implemented by the project itself.

---

# Multiple Paths

The simulation should be able to distribute drones between different available paths.

For example:

```text
             -> A -> C ->
START                  END
             -> B -> D ->
```

Instead of forcing every drone through the same route, the scheduler can distribute drones when doing so reduces congestion and the total number of turns.

This is particularly important when connections or zones have limited capacity.

---

# Scheduling

Finding a path is not enough to solve the complete problem.

The simulation also needs to decide **when** each drone should move.

The scheduler must consider:

* Zone occupancy.
* Connection occupancy.
* Zone capacity.
* Connection capacity.
* Other drones moving during the same turn.
* Waiting when necessary.
* Conflicts.
* Deadlocks.
* Restricted movement.
* Overall number of turns.

A drone may remain in its current zone when moving immediately would cause an invalid state.

---

# Deadlock Avoidance

The simulation must avoid situations where drones prevent one another from reaching the destination.

For example, if two drones occupy areas of the graph and each requires the other to move first, the scheduler must resolve the conflict instead of entering an infinite loop.

The simulation should always detect impossible situations and report them clearly.

---

# Parser Validation

The parser must reject invalid maps.

Examples of invalid input include:

* Missing number of drones.
* Zero or negative number of drones.
* Missing start zone.
* Missing end zone.
* Multiple start zones.
* Multiple end zones.
* Duplicate zone names.
* Invalid coordinates.
* Invalid zone names.
* Connections referencing unknown zones.
* Duplicate connections.
* Invalid metadata.
* Invalid zone types.
* Invalid capacities.
* Invalid map syntax.

Connections are considered duplicates even if their order is reversed.

For example:

```text
connection: A-B
connection: B-A
```

is invalid because both represent the same connection.

Parsing errors should clearly identify the line and the reason for the error.

---

# Unsolvable Maps

A map can be syntactically valid but still impossible to solve.

For example:

```text
start -> A

B -> end
```

If there is no connection between the two parts of the graph, the drones cannot reach the destination.

This is not a parsing error.

The program must detect the situation and report that the map is unsolvable.

---

# Output

The simulation must display the movement of the drones turn by turn.

There should be one output line for each simulation turn.

Movements on the same turn are separated by spaces.

The format is:

```text
D<ID>-<zone>
```

For example:

```text
D1-A D2-B D3-C
```

If a drone is currently travelling through a restricted connection, the output may represent the connection:

```text
D1-A-B
```

Delivered drones are no longer tracked after reaching the end zone.

The simulation ends when all drones have reached the destination.

---

# Example

For a simple map:

```text
nb_drones: 2

start_hub: start 0 0
end_hub: end 10 10

hub: A 2 2
hub: B 5 5

connection: start-A
connection: A-B
connection: B-end
```

A possible output is:

```text
D1-A D2-A
D1-B D2-B
D1-end D2-end
```

Both drones can move simultaneously when the capacities allow it.

---

# Visual Representation

The project provides visual feedback for the simulation.

The visualization can use terminal colors to represent different zones and/or states.

For example:

* Start zone.
* End zone.
* Normal zones.
* Restricted zones.
* Blocked zones.
* Priority zones.
* Drone positions.

The exact visual implementation depends on the project design, but the simulation must provide visual feedback as required by the subject.

---

# Optimization

The main objective is:

> Move all drones from the start zone to the end zone using the fewest possible simulation turns.

Program execution speed itself is not the primary concern.

The important measurement is the number of simulation turns required to deliver all drones.

The project should therefore optimize:

* Path selection.
* Drone distribution.
* Scheduling.
* Waiting decisions.
* Capacity usage.
* Conflict resolution.

---

# Benchmark Maps

The subject provides benchmark maps with known optimal turn counts.

## Easy

Expected optimal results:

```text
4
4
4
```

## Medium

Expected optimal results:

```text
8
10
6
```

## Hard

Expected optimal results:

```text
13
16
26
```

There is also an optional challenge map:

```text
43 turns
```

The optimization benchmark is separate from basic correctness.

A solution that does not reach the exact optimum is not automatically considered incorrect, provided that the simulation is correct.

---

# Testing

Tests should cover the different components of the project.

Recommended test categories include:

## Parser Tests

Test:

* Valid maps.
* Invalid maps.
* Missing values.
* Duplicate zones.
* Duplicate connections.
* Invalid capacities.
* Invalid zone types.
* Invalid metadata.
* Unknown zones.
* Unsolvable maps.

## Graph Tests

Test:

* Adding zones.
* Adding connections.
* Bidirectional connections.
* Duplicate connections.
* Neighbor lookup.
* Capacity information.

## Pathfinding Tests

Test:

* Simple paths.
* Multiple paths.
* Blocked zones.
* Restricted zones.
* Priority zones.
* Different path costs.
* Unreachable destinations.

## Simulation Tests

Test:

* One drone.
* Multiple drones.
* Simultaneous movement.
* Zone capacity.
* Connection capacity.
* Waiting.
* Restricted movement.
* Conflict resolution.
* Deadlock avoidance.
* Completion detection.

---

# Code Quality

The project follows Python coding standards.

The implementation should use:

* Python 3.10+.
* Type hints.
* `mypy`.
* `flake8`.
* PEP 257 docstrings.
* Proper exception handling.
* Proper resource management.
* Object-oriented design.

Run:

```bash
make lint
```

before submitting the project.

---

# Object-Oriented Design

The project is completely object-oriented.

Possible core classes include:

### `Zone`

Represents a zone in the map.

Responsibilities include:

* Name.
* Coordinates.
* Zone type.
* Capacity.
* Color.
* Current occupancy.

### `Connection`

Represents a connection between two zones.

Responsibilities include:

* Endpoints.
* Capacity.
* Movement information.
* Current occupancy.

### `Drone`

Represents one drone.

Responsibilities include:

* Drone ID.
* Current position.
* Current path.
* Destination.
* Movement state.
* Restricted-flight state.

### `Graph`

Represents the complete map.

Responsibilities include:

* Storing zones.
* Storing connections.
* Finding neighbors.
* Validating graph relationships.
* Providing graph information to pathfinding.

### `Pathfinder`

Responsible for calculating efficient routes.

### `Scheduler`

Responsible for deciding when drones move.

### `Simulator`

Responsible for running the turn-by-turn simulation.

### `Renderer`

Responsible for visual output.

---

# Error Handling

The application must handle errors gracefully.

Invalid user input should not result in an uncontrolled Python traceback being displayed as the normal user interface.

Errors should clearly explain what went wrong.

Examples:

```text
Error: invalid number of drones
```

```text
Error: unknown zone 'A'
```

```text
Error: duplicate connection 'A-B'
```

```text
Error: no path exists between start and end
```

---

# Resources

The project is based primarily on the official **Fly-in Drones** subject provided by the 42 curriculum.

Additional resources used during development should be documented here.

Examples of useful references include:

* Python documentation.
* Python type hints documentation.
* `flake8` documentation.
* `mypy` documentation.
* Python `unittest` or `pytest` documentation.
* Graph and pathfinding algorithm references.

Any external resources used to design or implement the project should be listed here with a short description of how they were used.

---

# Algorithm Choices

The project uses a custom graph representation rather than an external graph library.

The graph is composed of zones and bidirectional connections.

Pathfinding assigns movement costs according to the zone type:

| Zone type  |  Movement cost |
| ---------- | -------------: |
| Normal     |         1 turn |
| Priority   |         1 turn |
| Restricted |        2 turns |
| Blocked    | Not accessible |

The pathfinding algorithm evaluates available routes and avoids blocked zones.

For multiple drones, the scheduling system additionally considers:

* Zone capacity.
* Connection capacity.
* Existing drone positions.
* Simultaneous movements.
* Waiting.
* Conflicts.
* Restricted movements.

The final objective is to minimize the number of simulation turns needed for all drones to reach the end zone.

---

# Visual Representation Documentation

The visualization represents the state of the simulation as drones move through the network.

The implementation can use terminal colors and symbols to distinguish:

* Different zone types.
* Drone positions.
* The start zone.
* The end zone.
* Restricted areas.
* Blocked areas.
* Priority areas.

The visualization is updated during the simulation so that the user can follow the movement of the drones.

---

# Example Input and Expected Output

## Input

```text
nb_drones: 2

start_hub: start 0 0
end_hub: end 10 10

hub: A 2 2
hub: B 5 5

connection: start-A
connection: A-B
connection: B-end
```

## Expected Output

A valid simulation can produce output similar to:

```text
D1-A D2-A
D1-B D2-B
D1-end D2-end
```

The exact output may differ depending on the scheduling algorithm and capacity configuration, but all movements must respect the rules of the map.

---

# Restricted Zone Example

Consider:

```text
nb_drones: 1

start_hub: start 0 0
end_hub: end 10 10

hub: tunnel 5 5 zone=restricted

connection: start-tunnel
connection: tunnel-end
```

The movement into the restricted zone requires two turns.

Conceptually:

```text
Turn 1:
D1-start-tunnel

Turn 2:
D1-tunnel
```

The drone cannot spend an additional waiting turn on the restricted connection.

After arriving at the restricted zone, it can continue according to the normal simulation rules.

---

# Submission

Before submission, make sure that:

* The project is located at the repository root.
* The simulation runs correctly.
* The parser works correctly.
* Invalid maps are rejected.
* Unsolvable maps are detected.
* Drones reach the destination correctly.
* Zone capacities are respected.
* Connection capacities are respected.
* Restricted movements take two turns.
* Blocked zones are never used.
* Priority zones are handled.
* Multiple drones can move simultaneously.
* Deadlocks are avoided.
* Visual feedback works.
* `flake8` passes.
* `mypy` passes.
* The README is complete.
* The source code is fully understood by all team members.

---

# AI Usage

AI tools may be used as development assistance, but the project authors remain responsible for understanding, verifying, and maintaining all submitted code.

AI assistance may be used for:

* Understanding Python concepts.
* Understanding algorithms.
* Reviewing code.
* Identifying potential bugs.
* Improving documentation.
* Generating ideas for tests.
* Explaining errors.

All generated suggestions must be reviewed and tested by the project authors before being incorporated into the project.

The final implementation must be understood by the team, especially because the evaluation may include questions about the implementation or require a small code modification.

---

# Conclusion

**Fly-in Drones** combines graph modeling, pathfinding, scheduling, simulation, and optimization.

The main challenge is not simply finding a path from the start to the end. The program must coordinate multiple drones while respecting zone and connection capacities and minimizing the total number of simulation turns.

The project therefore focuses on three main components:

1. **Build and validate the graph.**
2. **Find efficient paths for the drones.**
3. **Schedule their movements efficiently and safely.**

The final result is a complete drone-routing simulation capable of handling different maps, movement restrictions, capacities, multiple simultaneous drones, and optimization requirements.
