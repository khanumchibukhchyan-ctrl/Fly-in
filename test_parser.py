
from src.parser.map_parser import parse_file


def main() -> None:
    graph = parse_file("test_map.txt")

    print(f"Number of drones: {graph.nb_drones}")
    print(f"Number of zones: {len(graph.zones)}")
    print(f"Number of connections: {len(graph.connections)}")

    print("\nZones:")
    for zone in graph.zones:
        print(
            f"Name: {zone.name}, "
            f"Role: {zone.zone_type}, "
            f"Type: {zone.zone_type_enum.value}, "
            f"x: {zone.x}, "
            f"y: {zone.y}, "
            f"Capacity: {zone.capacity}, "
            f"Color: {zone.color}"
        )

    print("\nConnections:")
    for connection in graph.connections:
        print(
            f"{connection.zone_a} -> {connection.zone_b}, "
            f"Capacity: {connection.capacity}"
        )


if __name__ == "__main__":
    main()
