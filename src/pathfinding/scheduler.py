from typing import List, Tuple, Dict
from src.model.graph import Graph
from src.model.drone import Drone

class Scheduler:
    def __init__(self, graph: Graph, paths: List[Tuple[List[str], float]]) -> None:
        self.graph = graph
        self.paths = paths
        self.drones: List[Drone] = []
        self.turns: List[str] = []
        
    def assign_drones(self) -> None:
        """Distribute drones across paths. Shorter paths get more drones."""
        for i in range(self.graph.nb_drones):
            path_index = i % len(self.paths)
            drone = Drone(i + 1, self.graph.start_hub)
            drone.path = self.paths[path_index][0]
            self.drones.append(drone)
    
    def simulate(self) -> List[str]:
        """Run the turn-by-turn simulation. Returns list of turn strings."""
        self.assign_drones()
  
        while True:
            
            connection_usage = {}
            all_arrived = True
            for drone in self.drones:
                if drone.path_index < len(drone.path) - 1:
                    all_arrived = False
                    break
            if all_arrived:
                break
  
            zone_occupancy = {}
            for drone in self.drones:
                if getattr(drone, "in_transit", False):
                    zone = drone.path[drone.path_index + 1]
                else:
                    zone = drone.path[drone.path_index]
                zone_occupancy[zone] = zone_occupancy.get(zone, 0) + 1
  
            self.drones.sort(key=lambda d: len(d.path) - d.path_index)

            movements = []
            for drone in self.drones:
                if drone.path_index >= len(drone.path) - 1:
                    continue

                if getattr(drone, "in_transit", False):
                    drone.path_index += 1
                    current_zone = drone.path[drone.path_index]
                    movements.append(f"D{drone.drone_id}-{current_zone}")
                    drone.in_transit = False
                    continue

                old_zone = drone.path[drone.path_index]
                next_zone = drone.path[drone.path_index + 1]

                # Check zone capacity
                max_allowed = self.graph.get_zone(next_zone).max_drones
                current_count = zone_occupancy.get(next_zone, 0)
                if current_count >= max_allowed:
                    continue

                # Check connection capacity
                conn = self.graph.get_connection(old_zone, next_zone)
                conn_key = frozenset({old_zone, next_zone})
                current_link_count = connection_usage.get(conn_key, 0)
                if current_link_count >= conn.max_link_capacity:
                    continue

                # All checks passed — move the drone!
                connection_usage[conn_key] = current_link_count + 1
                zone_occupancy[next_zone] = zone_occupancy.get(next_zone, 0) + 1
                zone_occupancy[old_zone] -= 1
                zone_type = self.graph.get_zone(next_zone).zone_type

                if zone_type == "restricted":
                    drone.in_transit = True
                    movements.append(f"D{drone.drone_id}-{old_zone}-{next_zone}")
                else:
                    drone.path_index += 1
                    movements.append(f"D{drone.drone_id}-{next_zone}")
  
            if not movements:
                raise Exception("DEADLOCK DETECTED")
                
            self.turns.append(" ".join(movements))
  
        return self.turns