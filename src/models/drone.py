class Drone:
    def __init__(
        self,
        id: int,
        current_zone: str,
        path: list[str]
    ) -> None:
        self.id = id
        self.current_zone = current_zone
        self.path = path
        self.path_index = 0
        self.in_transit = False
        self.transit_remaining = 0
        self.transit_destination: str | None = None
        self.transit_connection: tuple[str, str] | None = None