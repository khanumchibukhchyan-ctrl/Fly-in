import matplotlib.pyplot as plt

from src.models.connection import Connection
from src.models.drone import Drone
from src.models.graph import Graph
from src.models.zone import Zone, ZoneType


class Renderer:
    def __init__(self, graph: Graph, pause_time: float = 0.5) -> None:
        self.graph = graph
        self.pause_time = pause_time
        self.fig, self.ax = plt.subplots(figsize=(14, 9), dpi=120)
        if self.fig.canvas.manager is not None:
            self.fig.canvas.manager.set_window_title("Fly-in Simulation")
        plt.ion()

    def _resolve_zone_color(self, zone: Zone) -> str:
        type_colors: dict[ZoneType, str] = {
            ZoneType.NORMAL: "#FFF2B2",
            ZoneType.BLOCKED: "#D6D6D6",
            ZoneType.RESTRICTED: "#FFD6A5",
            ZoneType.PRIORITY: "gold",
        }
        if zone.zone_type == "start_hub":
            return "#A8E6CF"
        if zone.zone_type == "end_hub":
            return "#FFB7C5"
        if zone.color and zone.color != "none":
            return zone.color
        return type_colors.get(zone.zone_type_enum, "gray")

    def _draw_connection(
        self,
        connection: Connection,
        positions: dict[str, tuple[int, int]],
    ) -> None:
        x1, y1 = positions[connection.zone_a]
        x2, y2 = positions[connection.zone_b]

        self.ax.plot(
            [x1, x2],
            [y1, y2],
            color="gray",
            linewidth=3,
            zorder=1,
        )
        self.ax.text(
            (x1 + x2) / 2,
            (y1 + y2) / 2 + 0.12,
            f"Cap: {connection.capacity}",
            ha="center",
            fontsize=9,
            color="dimgray",
            bbox=dict(facecolor="white", alpha=0.8, edgecolor="none"),
            zorder=3,
        )

    def draw_map(
        self,
        drones: list[Drone] | None = None,
        turn: int = 0,
    ) -> None:
        if not plt.fignum_exists(self.fig.number):
            return

        self.ax.clear()
        positions: dict[str, tuple[int, int]] = {
            zone.name: (zone.x, zone.y) for zone in self.graph.zones
        }

        for connection in self.graph.connections:
            self._draw_connection(connection, positions)

        all_x: list[float] = [float(zone.x) for zone in self.graph.zones]
        all_y: list[float] = [float(zone.y) for zone in self.graph.zones]

        for zone in self.graph.zones:
            fill_color = self._resolve_zone_color(zone)
            edge_color = (
                zone.color
                if zone.color and zone.color != "none"
                else "black"
            )

            self.ax.scatter(
                zone.x,
                zone.y,
                color=fill_color,
                s=900,
                edgecolors=edge_color,
                linewidths=2.5,
                zorder=2,
            )
            self.ax.text(
                zone.x,
                zone.y - 0.35,
                zone.name,
                ha="center",
                fontsize=12,
                fontweight="bold",
                zorder=4,
            )

            if zone.zone_type in ("start_hub", "end_hub"):
                capacity_text = "Unlimited"
            else:
                capacity_text = f"Cap: {zone.capacity}"

            self.ax.text(
                zone.x,
                zone.y - 0.65,
                capacity_text,
                ha="center",
                fontsize=9,
                color="dimgray",
                zorder=4,
            )

        if drones is not None:
            drone_positions: dict[tuple[float, float], list[Drone]] = {}

            for drone in drones:
                if drone.in_transit:
                    if drone.transit_connection is None:
                        continue
                    zone_a, zone_b = drone.transit_connection
                    x1, y1 = positions[zone_a]
                    x2, y2 = positions[zone_b]
                    base_pos = ((x1 + x2) / 2, (y1 + y2) / 2)
                else:
                    zx, zy = positions[drone.current_zone]
                    base_pos = (float(zx), float(zy))

                drone_positions.setdefault(base_pos, []).append(drone)

            for (bx, by), group in drone_positions.items():
                for index, drone in enumerate(group):
                    offset = (index - (len(group) - 1) / 2) * 0.5
                    drone_x = bx + offset
                    drone_y = by + 0.45

                    all_x.append(drone_x)
                    all_y.append(drone_y)

                    self.ax.scatter(
                        drone_x,
                        drone_y,
                        color="#BFDFFF",
                        marker="o",
                        s=1100,
                        edgecolors="black",
                        linewidths=2.5,
                        zorder=5,
                    )
                    self.ax.text(
                        drone_x,
                        drone_y,
                        f"D{drone.id}",
                        ha="center",
                        va="center",
                        fontsize=12,
                        fontweight="bold",
                        color="black",
                        zorder=6,
                    )

        if all_x and all_y:
            padding = 1.5
            self.ax.set_xlim(min(all_x) - padding, max(all_x) + padding)
            self.ax.set_ylim(min(all_y) - padding, max(all_y) + padding)

        self.ax.set_title(
            f"FLY-IN SIMULATION - TURN {turn}",
            fontsize=18,
            fontweight="bold",
        )
        self.ax.tick_params(
            axis="both",
            which="both",
            bottom=False,
            left=False,
            labelbottom=False,
            labelleft=False,
        )
        self.ax.grid(True, linewidth=0.7, alpha=0.5)
        self.ax.set_aspect("equal")

        self.fig.tight_layout()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        if self.pause_time > 0:
            plt.pause(self.pause_time)
