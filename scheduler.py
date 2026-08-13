from typing import List, Tuple
from graph import Graph
from drone import Drone


class Scheduler:
    """Simple turn-by-turn drone simulator."""

    def __init__(
        self,
        graph: Graph,
        paths: List[Tuple[List[str], float]],
    ) -> None:
        self.graph = graph
        self.paths = paths
        self.drones: List[Drone] = []
        self.turns: List[str] = []

    def assign_drones(self) -> None:
        """Spread drones evenly across paths using round-robin."""
        assert self.graph.nb_drones is not None
        assert self.graph.start_hub is not None

        for i in range(self.graph.nb_drones):
            drone = Drone(i + 1, self.graph.start_hub)
            drone.path = self.paths[i % len(self.paths)][0]
            self.drones.append(drone)

    def simulate(self) -> List[str]:
        """Run the simulation turn by turn.

        Each turn, try to move each drone forward.
        A drone can move if the target zone is not full.
        Restricted zones take 2 turns to cross.

        Returns a list of turn strings.
        """
        self.assign_drones()

        while not self.all_drones_arrived():
            movements: List[str] = []

            # Count how many drones are in each zone
            zone_count: dict[str, int] = {}
            for drone in self.drones:
                if drone.in_transit:
                    zone = drone.path[drone.path_index + 1]
                else:
                    zone = drone.path[drone.path_index]
                zone_count[zone] = zone_count.get(zone, 0) + 1

            for drone in self.drones:
                # Skip drones that already arrived
                if drone.path_index >= len(drone.path) - 1:
                    continue

                # Finish 2-turn restricted transit
                if drone.in_transit:
                    drone.path_index += 1
                    drone.in_transit = False
                    movements.append(
                        f"D{drone.drone_id}"
                        f"-{drone.path[drone.path_index]}"
                    )
                    continue

                current = drone.path[drone.path_index]
                target = drone.path[drone.path_index + 1]

                # Is the target zone full?
                max_cap = self.graph.get_zone(target).max_drones
                if zone_count.get(target, 0) >= max_cap:
                    continue  # Wait

                # Move the drone
                zone_count[target] = zone_count.get(target, 0) + 1
                zone_count[current] -= 1

                zone_type = self.graph.get_zone(target).zone_type
                if zone_type == "restricted":
                    drone.in_transit = True
                    movements.append(
                        f"D{drone.drone_id}"
                        f"-{current}-{target}"
                    )
                else:
                    drone.path_index += 1
                    movements.append(f"D{drone.drone_id}-{target}")

            # If nobody moved, we are stuck
            if not movements:
                raise Exception("DEADLOCK DETECTED")

            self.turns.append(" ".join(movements))

        return self.turns

    def all_drones_arrived(self) -> bool:
        """Check if every drone reached the end."""
        for drone in self.drones:
            if drone.path_index < len(drone.path) - 1:
                return False
        return True
