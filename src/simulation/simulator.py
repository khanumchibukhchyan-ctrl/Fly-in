from src.models.zone import Zone, ZoneType
from src.models.graph import Graph
from src.models.drone import Drone
from src.models.connection import Connection
from src.pathfinding.pathfinder import find_path

def get_start_end(graph: Graph) -> tuple[str, str]:
	start: str | None = None
	end: str | None = None

	for zone in graph.zones:
		if zone.zone_type == "start_hub":
			start = zone.name
		elif zone.zone_type == "end_hub":
			end = zone.name

	if start is None or end is None:
		raise ValueError("Start or end hub not found")

	return start, end


def initialize_drones(graph: Graph) -> list[Drone]:
	start, end = get_start_end(graph)

	path = find_path(graph, start, end)

	if not path:
		raise ValueError("No available path from start to end")

	drones = []

	for drone_id in range(1, graph.nb_drones + 1):
		drone = Drone(
			drone_id,
			start,
			path.copy()
		)
		drones.append(drone)

	return drones


def get_connection_key(
    zone_a: str,
    zone_b: str
) -> tuple[str, str]:
    return (min(zone_a, zone_b), max(zone_a, zone_b))


def get_next_zone(drone: Drone) -> str | None:
    next_index = drone.path_index + 1

    if next_index >= len(drone.path):
        return None

    return drone.path[next_index]


def get_connection(
    graph: Graph,
    zone_a: str,
    zone_b: str
) -> Connection | None:
    for connection in graph.connections:
        if (
            connection.zone_a == zone_a
            and connection.zone_b == zone_b
        ):
            return connection

        if (
            connection.zone_a == zone_b
            and connection.zone_b == zone_a
        ):
            return connection

    return None


def count_zone_occupancy(
    drones: list[Drone],
    zone_name: str
) -> int:
    count = 0

    for drone in drones:
        if (
            drone.current_zone == zone_name
            and not drone.in_transit
        ):
            count += 1

    return count


def count_connection_occupancy(
    drones: list[Drone],
    zone_a: str,
    zone_b: str
) -> int:
    count = 0

    for drone in drones:
        if not drone.in_transit:
            continue

        connection = drone.transit_connection

        if connection is None:
            continue

        if (
            connection == (zone_a, zone_b)
            or connection == (zone_b, zone_a)
        ):
            count += 1

    return count


def get_zone(graph: Graph, zone_name: str) -> Zone | None:
    for zone in graph.zones:
        if zone.name == zone_name:
            return zone

    return None


def get_zone_capacity(graph: Graph, zone_name: str) -> int | None:
    zone = get_zone(graph, zone_name)

    if zone is None:
        return 0

    if zone.zone_type in ("start_hub", "end_hub"):
        return None

    return zone.capacity


def can_enter_zone(
    graph: Graph,
    drones: list[Drone],
    zone_name: str,
    planned_departures: dict[str, int],
    planned_arrivals: dict[str, int]
) -> bool:
    capacity = get_zone_capacity(graph, zone_name)

    if capacity is None:
        return True

    occupancy = count_zone_occupancy(drones, zone_name)

    occupancy -= planned_departures.get(zone_name, 0)
    occupancy += planned_arrivals.get(zone_name, 0)

    return occupancy < capacity


def can_use_connection(
    graph: Graph,
    drones: list[Drone],
    zone_a: str,
    zone_b: str,
    planned_entries: dict[tuple[str, str], int],
    planned_exits: dict[tuple[str, str], int]
) -> bool:
    connection = get_connection(graph, zone_a, zone_b)

    if connection is None:
        return False

    key = get_connection_key(zone_a, zone_b)

    occupancy = count_connection_occupancy(
        drones,
        zone_a,
        zone_b
    )

    occupancy -= planned_exits.get(key, 0)
    occupancy += planned_entries.get(key, 0)

    return occupancy < connection.capacity


def plan_moves(
    graph: Graph,
    drones: list[Drone]
) -> list[tuple[Drone, str, str]]:
    moves = []

    planned_departures: dict[str, int] = {}
    planned_arrivals: dict[str, int] = {}
    planned_entries: dict[tuple[str, str], int] = {}
    planned_exits: dict[tuple[str, str], int] = {}

    for drone in drones:
        if not drone.in_transit:
            continue

        destination = drone.transit_destination
        connection = drone.transit_connection

        if destination is None or connection is None:
            continue

        key = get_connection_key(*connection)

        planned_exits[key] = planned_exits.get(key, 0) + 1
        planned_arrivals[destination] = (
            planned_arrivals.get(destination, 0) + 1
        )

        moves.append((drone, destination, "arrive"))

    for drone in sorted(drones, key=lambda item: item.id):
        if drone.in_transit:
            continue

        next_zone = get_next_zone(drone)

        if next_zone is None:
            continue

        if not can_enter_zone(
            graph,
            drones,
            next_zone,
            planned_departures,
            planned_arrivals
        ):
            continue

        if not can_use_connection(
            graph,
            drones,
            drone.current_zone,
            next_zone,
            planned_entries,
            planned_exits
        ):
            continue

        zone = get_zone(graph, next_zone)

        if zone is None:
            continue

        action = "move"

        if zone.zone_type_enum == ZoneType.RESTRICTED:
            action = "transit"

        key = get_connection_key(drone.current_zone, next_zone)

        planned_departures[drone.current_zone] = (
            planned_departures.get(drone.current_zone, 0) + 1
        )

        planned_arrivals[next_zone] = (
            planned_arrivals.get(next_zone, 0) + 1
        )

        planned_entries[key] = planned_entries.get(key, 0) + 1

        moves.append((drone, next_zone, action))

    return moves


def apply_moves(
    moves: list[tuple[Drone, str, str]]
) -> None:
    for drone, destination, action in moves:

        if action == "move":
            drone.current_zone = destination
            drone.path_index += 1

        elif action == "transit":
            drone.in_transit = True
            drone.transit_destination = destination
            drone.transit_connection = (
                drone.current_zone,
                destination
            )
            drone.transit_remaining = 1

        elif action == "arrive":
            drone.current_zone = destination
            drone.path_index += 1
            drone.in_transit = False
            drone.transit_destination = None
            drone.transit_connection = None
            drone.transit_remaining = 0


def get_delivered_drones(
    drones: list[Drone],
    end_zone: str
) -> list[Drone]:
    delivered = []

    for drone in drones:
        if (
            drone.current_zone == end_zone
            and not drone.in_transit
        ):
            delivered.append(drone)

    return delivered


def print_turn(
    turn: int,
    moves: list[tuple[Drone, str, str]]
) -> None:
    print(f"Turn {turn}:")

    for drone, destination, action in moves:
        if action == "transit":
            connection = drone.transit_connection
            if connection is not None:
                print(
                    f"D{drone.id}-{connection[0]}-{connection[1]}"
                )

        elif action == "move" or action == "arrive":
            print(f"D{drone.id}-{destination}")


def run_simulation(graph: Graph) -> None:
    _, end_zone = get_start_end(graph)
    active_drones = initialize_drones(graph)
    turn = 0

    while active_drones:
        turn += 1
        moves = plan_moves(graph, active_drones)

        if not moves:
            raise RuntimeError(
                "Simulation stopped: no drones can move"
            )

        apply_moves(moves)
        print_turn(turn, moves)

        delivered = get_delivered_drones(
            active_drones,
            end_zone
        )

        for drone in delivered:
            active_drones.remove(drone)