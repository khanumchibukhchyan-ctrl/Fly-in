from src.models.zone import Zone
from src.models.graph import Graph
from src.models.drone import Drone
from src.pathfinding.pathfinder import find_path

def get_start_end(graph: Graph) -> tuple[str, str]:
	start = None
	end = None

	for zone in graph.zones:
		if zone.zone_type == "start_hub":
			start = zone.name
		elif zone.zone_type == "end_hub":
			end = zone.name

	if start is None or end is None:
		raise ValueError("Start or end hub not found")

	return start, end