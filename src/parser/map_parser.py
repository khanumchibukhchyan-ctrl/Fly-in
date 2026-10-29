from src.models.connection import Connection
from src.models.zone import Zone, ZoneType
from src.models.graph import Graph


def validate_metadata_brackets(
    line: str,
    line_number: int
) -> None:
    if line.count("[") > 1 or line.count("]") > 1:
        raise ValueError(
            f"Line {line_number}: "
            f"Multiple metadata blocks are not allowed: {line}"
        )
    if line.count("[") != line.count("]"):
        raise ValueError(
            f"Line {line_number}: "
            f"Invalid metadata brackets: {line}"
        )

    if "[" in line and "]" in line:
        if line.index("[") > line.index("]"):
            raise ValueError(
                f"Line {line_number}: "
                f"Invalid metadata brackets: {line}"
            )
    if "]" in line:
        after_metadata = line.split("]", 1)[1].strip()
        if after_metadata:
            raise ValueError(
                f"Line {line_number}: "
                f"Unexpected text after metadata: {line}"
            )


def parse_connection(
    main_part: str,
    line_number: int
) -> Connection:
    value = main_part.split(":", 1)[1].strip()
    parts = value.split("-")

    if len(parts) != 2:
        raise ValueError(
            f"Line {line_number}: "
            f"Invalid connection format: {value}"
        )

    zone_a = parts[0].strip()
    zone_b = parts[1].strip()

    if not zone_a or not zone_b:
        raise ValueError(
            f"Line {line_number}: "
            f"Invalid connection format: {value}"
        )

    return Connection(zone_a, zone_b)


def parse_main(
    main_part: str,
    line_number: int
) -> Zone:
    zone_components = main_part.split()

    if len(zone_components) != 4:
        raise ValueError(
            f"Line {line_number}: "
            f"Invalid zone format: {main_part}"
        )

    if zone_components[0] == "hub:":
        zone_type = "hub"
    elif zone_components[0] == "start_hub:":
        zone_type = "start_hub"
    elif zone_components[0] == "end_hub:":
        zone_type = "end_hub"

    else:
        raise ValueError(
            f"Line {line_number}: "
            f"Unknown zone type: {zone_components[0]}"
        )

    name = zone_components[1]

    if "-" in name:
        raise ValueError(
            f"Line {line_number}: Invalid zone name: {name}"
        )

    try:
        x = int(zone_components[2])
        y = int(zone_components[3])
    except ValueError:
        raise ValueError(
            f"Line {line_number}: Invalid zone coordinates: "
            f"{zone_components[2]}, {zone_components[3]}"
        )

    return Zone(name=name, x=x, y=y, zone_type=zone_type)


def parse_zone_metadata(
    metadata_part: str,
    zone: Zone,
    line_number: int
) -> Zone:
    parts = metadata_part.split()

    if not parts:
        raise ValueError(
            f"Line {line_number}: "
            f"Metadata block cannot be empty"
        )

    seen_keys = set()

    for part in parts:
        if "=" not in part:
            raise ValueError(
                f"Line {line_number}: "
                f"Invalid metadata format: {part}"
            )
        key, value = part.split("=", 1)

        if not key or not value:
            raise ValueError(
                f"Line {line_number}: "
                f"Invalid metadata format: {part}"
            )
        if key in seen_keys:
            raise ValueError(
                f"Line {line_number}: "
                f"Duplicate metadata key: {key}"
            )
        seen_keys.add(key)
        if key == "zone":
            try:
                zone.zone_type_enum = ZoneType(value)
            except ValueError:
                raise ValueError(
                    f"Line {line_number}: "
                    f"Invalid zone type: {value}"
                )
        elif key == "max_drones":
            if zone.zone_type in ("start_hub", "end_hub"):
                continue
            try:
                capacity = int(value)
            except ValueError:
                raise ValueError(
                    f"Line {line_number}: "
                    f"Invalid max_drones value: {value}"
                )
            if capacity <= 0:
                raise ValueError(
                    f"Line {line_number}: "
                    f"Invalid max_drones value: {value}"
                )
            zone.capacity = capacity
        elif key == "color":
            zone.color = value
        else:
            raise ValueError(
                f"Line {line_number}: "
                f"Unknown metadata: {key}"
            )
    return zone


def parse_connection_metadata(
    metadata_part: str,
    connection: Connection,
    line_number: int
) -> Connection:
    parts = metadata_part.split()

    if not parts:
        raise ValueError(
            f"Line {line_number}: "
            f"Metadata block cannot be empty"
        )

    seen_keys = set()

    for part in parts:
        if "=" not in part:
            raise ValueError(
                f"Line {line_number}: "
                f"Invalid metadata format: {part}"
            )
        key, value = part.split("=", 1)

        if not key or not value:
            raise ValueError(
                f"Line {line_number}: "
                f"Invalid metadata format: {part}"
            )
        if key in seen_keys:
            raise ValueError(
                f"Line {line_number}: "
                f"Duplicate metadata key: {key}"
            )
        seen_keys.add(key)
        if key == "max_link_capacity":
            try:
                capacity = int(value)
            except ValueError:
                raise ValueError(
                    f"Line {line_number}: "
                    f"Invalid max_link_capacity value: {value}"
                )
            if capacity <= 0:
                raise ValueError(
                    f"Line {line_number}: "
                    f"Invalid max_link_capacity value: {value}"
                )
            connection.capacity = capacity
        else:
            raise ValueError(
                f"Line {line_number}: "
                f"Unknown metadata: {key}"
            )

    return connection


def parse_line(line: str, graph: Graph, line_number: int) -> None:
    validate_metadata_brackets(line, line_number)

    if line.startswith("nb_drones:"):
        value = line.split(":", 1)[1].strip()
        try:
            nb_drones = int(value)
        except ValueError:
            raise ValueError(
                f"Line {line_number}: "
                f"Invalid nb_drones value: {value}"
            )
        if nb_drones <= 0:
            raise ValueError(
                f"Line {line_number}: "
                f"Invalid nb_drones value: {value}"
            )
        graph.nb_drones = nb_drones

    elif line.startswith("connection:"):
        main_part = line.split("[")[0].strip()
        connection = parse_connection(main_part, line_number)

        if connection.zone_a == connection.zone_b:
            raise ValueError(
                f"Line {line_number}: "
                f"A zone cannot connect to itself."
            )
        if "[" in line and "]" in line:
            metadata = line.split("[", 1)[1].split("]", 1)[0]
            connection = parse_connection_metadata(
                metadata,
                connection,
                line_number
            )

        if not any(
            zone.name == connection.zone_a
            for zone in graph.zones
        ):
            raise ValueError(
                f"Line {line_number}: Unknown zone: {connection.zone_a}"
            )

        if not any(
            zone.name == connection.zone_b
            for zone in graph.zones
        ):
            raise ValueError(
                f"Line {line_number}: Unknown zone: {connection.zone_b}"
            )
        for existing_connection in graph.connections:
            if (
                existing_connection.zone_a == connection.zone_a
                and existing_connection.zone_b == connection.zone_b
            ) or (
                existing_connection.zone_a == connection.zone_b
                and existing_connection.zone_b == connection.zone_a
            ):
                raise ValueError(
                    f"Line {line_number}: Duplicate connection: "
                    f"{connection.zone_a}-{connection.zone_b}"
                )
        graph.add_connection(connection)

    elif line.startswith(("hub:", "start_hub:", "end_hub:")):
        main_part = line.split("[", 1)[0].strip()
        zone = parse_main(main_part, line_number)

        if "[" in line and "]" in line:
            metadata = line.split("[", 1)[1].split("]", 1)[0]
            zone = parse_zone_metadata(
                metadata,
                zone,
                line_number
            )

        for existing_zone in graph.zones:
            if existing_zone.name == zone.name:
                raise ValueError(
                    f"Line {line_number}: "
                    f"Duplicate zone name: {zone.name}"
                )

        graph.add_zone(zone)
    else:
        raise ValueError(f"Line {line_number}: Unknown line: {line}")


def parse_file(filename: str) -> Graph:
    graph = Graph()
    start_flag = False
    end_flag = False

    with open(filename) as file:
        first_line = file.readline().strip()

        if not first_line.startswith("nb_drones:"):
            raise ValueError("Line 1: First line must define nb_drones")

        parts = first_line.split(":", 1)

        if (
            len(parts) != 2
            or parts[0].strip() != "nb_drones"
            or not parts[1].strip()
        ):
            raise ValueError("Line 1: Invalid nb_drones format")

        parse_line(first_line, graph, 1)

        for line_number, line in enumerate(file, start=2):
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            if line.startswith("nb_drones:"):
                raise ValueError(
                    f"Line {line_number}: "
                    "nb_drones must be defined only on the first line"
                )

            if line.startswith("start_hub:"):
                if start_flag:
                    raise ValueError(
                        f"Line {line_number}: "
                        "Multiple start hubs are not allowed."
                    )
                start_flag = True

            elif line.startswith("end_hub:"):
                if end_flag:
                    raise ValueError(
                        f"Line {line_number}: "
                        "Multiple end hubs are not allowed."
                    )
                end_flag = True

            parse_line(line, graph, line_number)
        if not start_flag:
            raise ValueError("Line 1: Missing start hub.")

        if not end_flag:
            raise ValueError("Line 1: Missing end hub.")
    return graph
