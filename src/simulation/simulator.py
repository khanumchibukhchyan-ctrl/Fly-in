from src.models.zone import Zone, ZoneType
from src.models.graph import Graph
from src.models.drone import Drone
from src.models.connection import Connection
from src.pathfinding.pathfinder import find_path


class Simulation:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.drones: list[Drone] = []
        self.turn = 0

    def get_start_end(self) -> tuple[str, str]:
        start: str | None = None
        end: str | None = None

        for zone in self.graph.zones:
            if zone.zone_type == "start_hub":
                start = zone.name
            elif zone.zone_type == "end_hub":
                end = zone.name

        if start is None or end is None:
            raise ValueError("Start or end hub not found")

        return start, end

    def initialize_drones(self) -> list[Drone]:
        start, end = self.get_start_end()

        path = find_path(self.graph, start, end)

        if not path:
            raise ValueError("No available path from start to end")

        drones = []

        for drone_id in range(1, self.graph.nb_drones + 1):
            drone = Drone(
                drone_id,
                start,
                path.copy()
            )
            drones.append(drone)

        return drones

    def get_connection_key(
        self,
        zone_a: str,
        zone_b: str
    ) -> tuple[str, str]:
        return (min(zone_a, zone_b), max(zone_a, zone_b))

    def get_next_zone(self, drone: Drone) -> str | None:
        next_index = drone.path_index + 1

        if next_index >= len(drone.path):
            return None

        return drone.path[next_index]

    def get_connection(
        self,
        zone_a: str,
        zone_b: str
    ) -> Connection | None:
        for connection in self.graph.connections:
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
        self,
        zone_name: str
    ) -> int:
        count = 0

        for drone in self.drones:
            if (
                drone.current_zone == zone_name
                and not drone.in_transit
            ):
                count += 1

        return count

    def count_connection_occupancy(
        self,
        zone_a: str,
        zone_b: str
    ) -> int:
        count = 0

        for drone in self.drones:
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

    def get_zone(self, zone_name: str) -> Zone | None:
        for zone in self.graph.zones:
            if zone.name == zone_name:
                return zone

        return None

    def get_zone_capacity(self, zone_name: str) -> int | None:
        zone = self.get_zone(zone_name)

        if zone is None:
            return 0

        if zone.zone_type in ("start_hub", "end_hub"):
            return None

        return zone.capacity

    def can_enter_zone(
        self,
        zone_name: str,
        planned_departures: dict[str, int],
        planned_arrivals: dict[str, int]
    ) -> bool:
        capacity = self.get_zone_capacity(zone_name)

        if capacity is None:
            return True

        occupancy = self.count_zone_occupancy(zone_name)

        occupancy -= planned_departures.get(zone_name, 0)
        occupancy += planned_arrivals.get(zone_name, 0)

        return occupancy < capacity

    def can_use_connection(
        self,
        zone_a: str,
        zone_b: str,
        planned_entries: dict[tuple[str, str], int],
        planned_exits: dict[tuple[str, str], int]
    ) -> bool:
        connection = self.get_connection(zone_a, zone_b)

        if connection is None:
            return False

        key = self.get_connection_key(zone_a, zone_b)

        occupancy = self.count_connection_occupancy(
            zone_a,
            zone_b
        )

        occupancy -= planned_exits.get(key, 0)
        occupancy += planned_entries.get(key, 0)

        return occupancy < connection.capacity

    def plan_moves(self) -> list[tuple[Drone, str, str]]:
        moves = []

        planned_departures: dict[str, int] = {}
        planned_arrivals: dict[str, int] = {}
        planned_entries: dict[tuple[str, str], int] = {}
        planned_exits: dict[tuple[str, str], int] = {}

        for drone in self.drones:
            if not drone.in_transit:
                continue

            destination = drone.transit_destination
            connection = drone.transit_connection

            if destination is None or connection is None:
                continue

            key = self.get_connection_key(*connection)

            planned_exits[key] = planned_exits.get(key, 0) + 1
            planned_arrivals[destination] = (
                planned_arrivals.get(destination, 0) + 1
            )

            moves.append((drone, destination, "arrive"))

        for drone in sorted(self.drones, key=lambda item: item.id):
            if drone.in_transit:
                continue

            next_zone = self.get_next_zone(drone)

            if next_zone is None:
                continue

            if not self.can_enter_zone(
                next_zone,
                planned_departures,
                planned_arrivals
            ):
                continue

            if not self.can_use_connection(
                drone.current_zone,
                next_zone,
                planned_entries,
                planned_exits
            ):
                continue

            zone = self.get_zone(next_zone)

            if zone is None:
                continue

            action = "move"

            if zone.zone_type_enum == ZoneType.RESTRICTED:
                action = "transit"

            key = self.get_connection_key(drone.current_zone, next_zone)

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
        self,
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
        self,
        end_zone: str
    ) -> list[Drone]:
        delivered = []

        for drone in self.drones:
            if (
                drone.current_zone == end_zone
                and not drone.in_transit
            ):
                delivered.append(drone)

        return delivered

    def print_turn(
        self,
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

    def run(self) -> None:
        _, end_zone = self.get_start_end()
        self.drones = self.initialize_drones()

        while self.drones:
            self.turn += 1
            moves = self.plan_moves()

            if not moves:
                raise RuntimeError(
                    "Simulation stopped: no drones can move"
                )

            self.apply_moves(moves)
            self.print_turn(self.turn, moves)

            delivered = self.get_delivered_drones(end_zone)

            for drone in delivered:
                self.drones.remove(drone)
