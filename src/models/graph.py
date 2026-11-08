from src.models.zone import Zone
from src.models.connection import Connection


class Graph:
    def __init__(self) -> None:
        self.zones: list[Zone] = []
        self.connections: list[Connection] = []
        self.nb_drones: int = 0
        self.adjacency: dict[str, list[str]] = {}

    def add_zone(self, zone: Zone) -> None:
        self.zones.append(zone)

    def add_connection(self, connection: Connection) -> None:
        self.connections.append(connection)

        if connection.zone_a not in self.adjacency:
            self.adjacency[connection.zone_a] = []

        if connection.zone_b not in self.adjacency:
            self.adjacency[connection.zone_b] = []

        if connection.zone_b not in self.adjacency[connection.zone_a]:
            self.adjacency[connection.zone_a].append(connection.zone_b)

        if connection.zone_a not in self.adjacency[connection.zone_b]:
            self.adjacency[connection.zone_b].append(connection.zone_a)

    def get_neighbors(self, zone_name: str) -> list[str]:
        return self.adjacency.get(zone_name, [])