import heapq

from src.models.connection import Connection
from src.models.graph import Graph
from src.models.zone import Zone, ZoneType


def is_better(
    new_distance: tuple[float, int],
    old_distance: tuple[float, int]
) -> bool:
    if new_distance[0] < old_distance[0]:
        return True

    if new_distance[0] == old_distance[0]:
        return new_distance[1] > old_distance[1]

    return False


def get_connection(
    graph: Graph,
    zone_a: str,
    zone_b: str
) -> Connection | None:
    for connection in graph.connections:
        if (
            (connection.zone_a == zone_a and connection.zone_b == zone_b)
            or (connection.zone_a == zone_b and connection.zone_b == zone_a)
        ):
            return connection
    return None


def step_cost(
    graph: Graph,
    current_zone: str,
    neighbor: Zone,
    edge_loads: dict[tuple[str, str], int] | None = None,
    zone_loads: dict[str, int] | None = None
) -> float:
    if (neighbor.zone_type_enum == ZoneType.RESTRICTED):
        base_cost = 2.0    
    else:
        base_cost = 1.0
    penalty = 0.0

    if neighbor.zone_type not in ("start_hub", "end_hub"):
        zone_cap = max(1, neighbor.capacity)
        if zone_loads:
            z_load = zone_loads.get(neighbor.name, 0)
        else:
            z_load = 0
        penalty += (z_load / zone_cap) * 1.5

    conn = get_connection(graph, current_zone, neighbor.name)
    if conn is not None:
        conn_cap = max(1, conn.capacity)
        key = (min(current_zone, neighbor.name),
               max(current_zone, neighbor.name))
        e_load = edge_loads.get(key, 0) if edge_loads else 0
        penalty += (e_load / conn_cap) * 1.5

    return base_cost + penalty


def find_path(
    graph: Graph,
    start: str,
    end: str,
    edge_loads: dict[tuple[str, str], int] | None = None,
    zone_loads: dict[str, int] | None = None
) -> list[str]:
    zones_by_name = {
        zone.name: zone
        for zone in graph.zones
    }

    if start not in zones_by_name or end not in zones_by_name:
        return []

    distances: dict[str, tuple[float, int]] = {
        zone.name: (float("inf"), 0)
        for zone in graph.zones
    }
    distances[start] = (0.0, 0)

    previous: dict[str, str | None] = {
        zone.name: None
        for zone in graph.zones
    }

    priority_queue: list[tuple[float, int, str]] = [(0.0, 0, start)]

    while priority_queue:
        popped_cost, negative_priority, current_zone = (
            heapq.heappop(priority_queue)
        )

        current_distance = (popped_cost, -negative_priority)

        if current_distance != distances[current_zone]:
            continue

        if current_zone == end:
            break

        for neighbor_name in graph.get_neighbors(current_zone):
            neighbor = zones_by_name[neighbor_name]

            if neighbor.zone_type_enum == ZoneType.BLOCKED:
                continue

            movement_cost = step_cost(
                graph,
                current_zone,
                neighbor,
                edge_loads=edge_loads,
                zone_loads=zone_loads
            )

            priority_bonus = 1 if (
                neighbor.zone_type_enum == ZoneType.PRIORITY
            ) else 0

            new_distance = (
                current_distance[0] + movement_cost,
                current_distance[1] + priority_bonus
            )

            if is_better(new_distance, distances[neighbor_name]):
                distances[neighbor_name] = new_distance
                previous[neighbor_name] = current_zone

                heapq.heappush(
                    priority_queue,
                    (
                        new_distance[0],
                        -new_distance[1],
                        neighbor_name
                    )
                )

    if distances[end][0] == float("inf"):
        return []

    path: list[str] = []
    current: str | None = end

    while current is not None:
        path.append(current)
        current = previous[current]

    path.reverse()
    return path
