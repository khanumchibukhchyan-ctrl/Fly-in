from src.models.zone import Zone
from src.models.connection import Connection


class Graph:
    def __init__(self):
        self.zones: list[Zone] = []
        self.connections: list[Connection] = []
        self.nb_drones: int = 0

    def add_zone(self, zone: Zone) -> None:
        self.zones.append(zone)

    def add_connection(self, connection: Connection) -> None:
        self.connections.append(connection)
