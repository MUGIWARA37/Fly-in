from typing import Dict, List, Set
from src.parsing.parser import MapParser
from .zone import Zone
from .connection import Connection

class Graph:
    def __init__(self,parser: MapParser) -> None:
        self.nb_drones = parser.nb_drones
        self.start_hub = parser.start_hub_name
        self.end_hub = parser.end_hub_name
        self.zones: Dict[str, Zone] = {}
        self.connections: List[Connection] = []
        
        self._build_graph(parser)
        
    
    def _build_graph(self,parser: MapParser) -> None:
        for name, zone in parser.zones.items():
            new_zone = Zone(name, zone["x"], zone["y"],zone["zone_type"],
                            zone["color"], zone["max_drones"],
                            zone["is_start"], zone["is_end"])
            self.zones[name] = new_zone
            
        for conn_data in parser.connections:
            z1_obj = self.zones[conn_data["zone1"]]
            z2_obj = self.zones[conn_data["zone2"]]
            
            new_connection = Connection(z1_obj, z2_obj, conn_data["max_link_capacity"])
            self.connections.append(new_connection)
            
    def get_zone(self, name: str) -> Zone:
        return (self.zones[name])
    
    def get_neighbors(self, zone_name: str) -> List[Zone]:
        lst = []

        for connection in self.connections:
            if connection.zone_a.name == zone_name:
                lst.append(connection.zone_b)

            elif connection.zone_b.name == zone_name:
                lst.append(connection.zone_a)
        
        return lst

    def get_move_cost(self, zone_name: str) -> float:
        """Returns the movement cost to enter a zone based on its type."""
        zone = self.zones[zone_name]
        costs: Dict[str, float] = {
            "normal": 1.0,
            "restricted": 2.0,
            "priority": 0.9,
            "blocked": float("inf")
        }
        return costs.get(zone.zone_type, 1.0)
    
    def get_connection(self, zone_name_1: str, zone_name_2: str) -> Connection:
        for conn in self.connections:
            names = {conn.zone_a.name, conn.zone_b.name}
            if zone_name_1 in names and zone_name_2 in names:
                return conn
        raise ValueError("Connection not found")
        