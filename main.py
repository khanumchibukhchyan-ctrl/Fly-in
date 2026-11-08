import sys

from src.parser.map_parser import parse_file
from src.simulation.simulator import run_simulation


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <map_file>")
        return

    try:
        graph = parse_file(sys.argv[1])
        run_simulation(graph)
    except (ValueError, RuntimeError, OSError) as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()
