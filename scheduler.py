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
        """Spread drones across paths.

        Each drone is assigned to the path with the lowest
        estimated finish time. The formula is:
            score = path_cost + (drones_already_on_path * 1.5)
        This naturally balances load across paths.
        """
        assert self.graph.nb_drones is not None
        assert self.graph.start_hub is not None

        drones_per_path = [0] * len(self.paths)

        for i in range(self.graph.nb_drones):
            # Find the path with the best score
            best_path = 0
            best_score = float("inf")

            for p in range(len(self.paths)):
                cost = self.paths[p][1]
                load = drones_per_path[p] * 1.5
                score = cost + load

                if score < best_score:
                    best_score = score
                    best_path = p

            # Create the drone and assign it
            drones_per_path[best_path] += 1
            drone = Drone(i + 1, self.graph.start_hub)
            drone.path = self.paths[best_path][0]
            self.drones.append(drone)

    def simulate(self) -> List[str]:
        """Run the simulation turn by turn.

        Each turn:
        1. Handle drones finishing restricted-zone transit
        2. Try to move each waiting drone forward
        3. Record all movements as a single turn string

        Returns a list of turn strings.
        """
        self.assign_drones()

        while not self.all_drones_arrived():
            movements: List[str] = []

            # Snapshot: count how many drones are in each zone
            zone_count: dict[str, int] = {}
            for drone in self.drones:
                if drone.in_transit:
                    zone = drone.path[drone.path_index + 1]
                else:
                    zone = drone.path[drone.path_index]
                zone_count[zone] = zone_count.get(zone, 0) + 1

            # Track connection usage this turn
            conn_count: dict[frozenset[str], int] = {}

            # Process drones closest to the end first
            ordered = sorted(
                self.drones,
                key=lambda d: len(d.path) - d.path_index,
            )

            for drone in ordered:
                # Skip drones that already arrived
                if drone.path_index >= len(drone.path) - 1:
                    continue

                # --- RESTRICTED ZONE TRANSIT ---
                # If a drone entered a restricted zone last turn,
                # it finishes its 2-turn transit now.
                if drone.in_transit:
                    drone.path_index += 1
                    drone.in_transit = False
                    zone_name = drone.path[drone.path_index]
                    movements.append(
                        f"D{drone.drone_id}-{zone_name}"
                    )
                    continue

                # --- TRY TO MOVE FORWARD ---
                current = drone.path[drone.path_index]
                target = drone.path[drone.path_index + 1]

                # Check 1: Is the target zone full?
                max_cap = self.graph.get_zone(target).max_drones
                if zone_count.get(target, 0) >= max_cap:
                    continue  # Wait this turn

                # Check 2: Is the connection full?
                link = frozenset({current, target})
                conn = self.graph.get_connection(current, target)
                if conn_count.get(link, 0) >= conn.max_link_capacity:
                    continue  # Wait this turn

                # All clear — move the drone
                conn_count[link] = conn_count.get(link, 0) + 1
                zone_count[target] = zone_count.get(target, 0) + 1
                zone_count[current] -= 1

                zone_type = self.graph.get_zone(target).zone_type
                if zone_type == "restricted":
                    # Entering a restricted zone: takes 2 turns
                    drone.in_transit = True
                    movements.append(
                        f"D{drone.drone_id}-{current}-{target}"
                    )
                else:
                    # Normal move: instant arrival
                    drone.path_index += 1
                    movements.append(
                        f"D{drone.drone_id}-{target}"
                    )

            # If nobody moved, we are stuck
            if not movements:
                raise Exception("DEADLOCK DETECTED")

            self.turns.append(" ".join(movements))

        return self.turns

    def all_drones_arrived(self) -> bool:
        """Check if every drone has reached the end of its path."""
        for drone in self.drones:
            if drone.path_index < len(drone.path) - 1:
                return False
        return True
