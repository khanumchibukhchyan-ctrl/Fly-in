import matplotlib.pyplot as plt

from src.models.graph import Graph
from src.models.zone import ZoneType
from src.models.drone import Drone


class Renderer:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.fig, self.ax = plt.subplots(figsize=(14, 9), dpi=120)
        self.fig.canvas.manager.set_window_title("Fly-in Simulation")
        plt.ion()

    def draw_map(
        self,
        drones: list[Drone] | None = None,
        turn: int = 0
    ) -> None:
        self.ax.clear()

        positions: dict[str, tuple[int, int]] = {}

        for zone in self.graph.zones:
            positions[zone.name] = (zone.x, zone.y)

        for connection in self.graph.connections:
            x1, y1 = positions[connection.zone_a]
            x2, y2 = positions[connection.zone_b]

            self.ax.plot(
                [x1, x2],
                [y1, y2],
                color="gray",
                linewidth=3,
                zorder=1
            )

            self.ax.text(
                (x1 + x2) / 2,
                (y1 + y2) / 2 + 0.12,
                f"Cap: {connection.capacity}",
                ha="center",
                fontsize=9,
                color="dimgray",
                bbox=dict(facecolor="white", alpha=0.8, edgecolor="none"),
                zorder=3
            )
        colors: dict[ZoneType, str] = {
            ZoneType.NORMAL: "#FFF2B2",
            ZoneType.BLOCKED: "#D6D6D6",
            ZoneType.RESTRICTED: "#FFD6A5",
            ZoneType.PRIORITY: "gold"
        }

        for zone in self.graph.zones:
            color = colors.get(zone.zone_type_enum, "gray")

            if zone.zone_type == "start_hub":
                color = "#A8E6CF"
            elif zone.zone_type == "end_hub":
                color = "#FFB7C5"

            self.ax.scatter(
                zone.x,
                zone.y,
                color=color,
                s=900,
                edgecolors="black",
                linewidths=2,
                zorder=2
            )

            self.ax.text(
                zone.x,
                zone.y - 0.35,
                zone.name,
                ha="center",
                fontsize=12,
                fontweight="bold",
                zorder=4
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
                zorder=4
    )
        if drones is not None:
            drone_positions: dict[
                tuple[float, float],
                list[Drone]
            ] = {}

            for drone in drones:
                if drone.in_transit:
                    transit_connection = drone.transit_connection

                    if transit_connection is None:
                        continue

                    zone_a, zone_b = transit_connection

                    x1, y1 = positions[zone_a]
                    x2, y2 = positions[zone_b]

                    position = (
                        (x1 + x2) / 2,
                        (y1 + y2) / 2
                    )
                else:
                    zone_position = positions[drone.current_zone]
                    position = (
                        float(zone_position[0]),
                        float(zone_position[1])
                    )

                drone_positions.setdefault(
                    position, []
                ).append(drone)

            for position, group in drone_positions.items():
                x, y = position

                for index, drone in enumerate(group):
                    offset = (
                        index - (len(group) - 1) / 2
                    ) * 0.5

                    drone_x = x + offset
                    drone_y = y + 0.45

                    self.ax.scatter(
                        drone_x,
                        drone_y,
                        color="#BFDFFF",
                        marker="o",
                        s=1100,
                        edgecolors="black",
                        linewidths=2.5,
                        zorder=5
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
                        zorder=6
                    )

        x_values = [zone.x for zone in self.graph.zones]
        y_values = [zone.y for zone in self.graph.zones]

        padding = 1.5

        self.ax.set_xlim(
            min(x_values) - padding,
            max(x_values) + padding
        )
        self.ax.set_ylim(
            min(y_values) - padding,
            max(y_values) + padding
        )

        self.ax.set_title(
            f"FLY-IN SIMULATION - TURN {turn}",
            fontsize=18,
            fontweight="bold"
        )
        self.ax.set_xlabel("", fontsize=13)
        self.ax.set_ylabel("", fontsize=13)

        self.ax.tick_params(
            axis="both",
            color="black",
            labelcolor="white",
            )
        self.ax.grid(True, linewidth=0.7, alpha=0.5)
        self.ax.set_aspect("equal")

        self.fig.tight_layout()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        plt.pause(1.5)
