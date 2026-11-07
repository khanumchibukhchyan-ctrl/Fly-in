import heapq

from src.models.graph import Graph
from src.models.zone import ZoneType

def is_better(
	new_distance: tuple[float, int],
	old_distance: tuple[float, int]		
) -> bool:
	if new_distance[0] < old_distance[0]:
		return True

	if new_distance[0] == old_distance[0]:
		return new_distance[1] > old_distance[1]

	return False

def find_path(
		graph: Graph,
		start: str,
		end: str
) -> list[str] :
	zone_names = {
		zone.name
		for zone in graph.zones
	}

	if start not in zone_names or end not in zone_names:
		return []

	zones_by_name = {
		zone.name: zone
		for zone in graph.zones
	}

	distances = {
		zone.name: (float("inf"), 0)
		for zone in graph.zones
	}

	distances[start] = (0, 0)

	previous: dict[str, str | None] = {
		zone.name: None
		for zone in graph.zones
	}

	priority_queue = [(0, 0, start)]

	while priority_queue:
		current_distance, negative_priority, current_zone = (
			heapq.heappop(priority_queue)
		)

		current_distance = (current_cost, -negative_priority)
		if current_distance != distances[current_zone]:
			continue

		if current_zone == end:
			break

		for neighbor_name in graph.get_neighbors(current_zone):
			neighbor = zones_by_name[neighbor_name]

			if neighbor.zone_type_enum == ZoneType.BLOCKED:
				continue

			if neighbor.zone_type_enum == ZoneType.RESTRICTED:
				movement_cost = 2
			else:
				movement_cost = 1

			priority_bonus = 0

			if neighbor.zone_type_enum == ZoneType.PRIORITY:
				priority_bonus = 1

			new_distance = (
				current_distance[0] + movement_cost,
				current_distance[1] + priority_bonus
			)

			if is_better(new_distance, distances[neighbor_name]):
				distances[neighbor_name] = new_distance
				previous[neighbor_name] = current_zone

				heapq.heappush(
					priority_queue,
					(
						new_distance[0],
						-new_distance[1],
						neighbor_name
					)
				)

			if distances[end][0] == float("inf"):
				return []

			path = []
			current = end

			while current is not None:
				path.append(current)
				current = previous[current]

			path.reverse()

			return path