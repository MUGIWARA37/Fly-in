from typing import List, Tuple
from graph import Graph
from drone import Drone


class Scheduler:
    """Simple turn-by-turn drone simulator."""

    def __init__(
        self, graph: Graph, paths: List[Tuple[List[str], float]]
    ) -> None:
        self.graph = graph
        self.paths = paths
        self.drones: List[Drone] = []
        self.turns: List[str] = []

    def assign_drones(self) -> None:
        """Spread drones across paths using a greedy heuristic."""
        path_counts = [0] * len(self.paths)

        assert self.graph.nb_drones is not None
        assert self.graph.start_hub is not None
        for i in range(self.graph.nb_drones):
            # Pick the path with lowest estimated finish time
            best = min(
                range(len(self.paths)),
                key=lambda idx: self.paths[idx][1] + path_counts[idx] * 1.5,
            )
            path_counts[best] += 1
            drone = Drone(i + 1, self.graph.start_hub)
            drone.path = self.paths[best][0]
            self.drones.append(drone)

    def simulate(self) -> List[str]:
        """Run simulation. Returns list of turn strings."""
        self.assign_drones()

        while not all(d.path_index >= len(d.path) - 1 for d in self.drones):
            movements = []
            zone_occupancy: dict[str, int] = {}
            conn_usage: dict[frozenset[str], int] = {}

            # Count current occupancy
            for d in self.drones:
                if d.in_transit:
                    z = d.path[d.path_index + 1]
                else:
                    z = d.path[d.path_index]
                zone_occupancy[z] = zone_occupancy.get(z, 0) + 1

            # Process drones: snectihortest remaining path first
            for drone in sorted(
                self.drones, key=lambda d: len(d.path) - d.path_index
            ):
                if drone.path_index >= len(drone.path) - 1:
                    continue

                # Finish 2-turn restricted transit
                if drone.in_transit:
                    drone.path_index += 1
                    drone.in_transit = False
                    movements.append(
                        f"D{drone.drone_id}-{drone.path[drone.path_index]}"
                    )
                    continue

                old = drone.path[drone.path_index]
                nxt = drone.path[drone.path_index + 1]

                # Check zone capacity
                max_cap = self.graph.get_zone(nxt).max_drones
                if zone_occupancy.get(nxt, 0) >= max_cap:
                    continue

                # Check connection capacity
                key = frozenset({old, nxt})
                conn = self.graph.get_connection(old, nxt)
                if conn_usage.get(key, 0) >= conn.max_link_capacity:
                    continue

                # Move
                conn_usage[key] = conn_usage.get(key, 0) + 1
                zone_occupancy[nxt] = zone_occupancy.get(nxt, 0) + 1
                zone_occupancy[old] -= 1

                if self.graph.get_zone(nxt).zone_type == "restricted":
                    drone.in_transit = True
                    movements.append(f"D{drone.drone_id}-{old}-{nxt}")
                else:
                    drone.path_index += 1
                    movements.append(f"D{drone.drone_id}-{nxt}")

            if not movements:
                raise Exception("DEADLOCK DETECTED")

            self.turns.append(" ".join(movements))

        return self.turns
