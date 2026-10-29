from enum import Enum


class ZoneType(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Zone:
    def __init__(
        self,
        name: str,
        zone_type: str,
        x: int,
        y: int,
        zone_type_enum: ZoneType = ZoneType.NORMAL,
        capacity: int = 1,
        color: str = "none",
    ) -> None:
        self.name = name
        self.zone_type = zone_type
        self.x = x
        self.y = y
        self.zone_type_enum = zone_type_enum
        self.capacity = capacity
        self.color = color
