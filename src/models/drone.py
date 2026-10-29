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
