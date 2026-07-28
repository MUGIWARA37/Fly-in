from typing import Dict, List
from .tokens import *
from .exceptions import ParseError

class MapParser:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.nb_drones: int | None = None
        self.start_hub_count:int = 0
        self.end_hub_count:int = 0
        self.zones:Dict[str, dict] = {}
        self.connections:List[Dict] = []
        self.current_line:int = 0
        self.start_hub_name: str | None = None
        self.end_hub_name: str | None = None
        self.seen_connections: set = set()

    def parse(self) -> None:                                                   
        with open(self.filepath, "r") as f:                                    
            for line_num, line in enumerate(f, start=1):                       
                self.current_line = line_num                                   
                line = line.strip()                                            
                if not line or line.startswith("#"):                           
                    continue                                                   

                try:

                    if line.startswith("nb_drones:"):
                        self._parse_nb_drones(line)
                    elif line.startswith("start_hub:"):
                        self._parse_hub(line, hub_type="start")
                    elif line.startswith("end_hub:"):
                        self._parse_hub(line, hub_type="end")
                    elif line.startswith("hub:"):
                        self._parse_hub(line, hub_type="normal")
                    elif line.startswith("connection:"):
                        self._parse_connection(line)
                    else:
                        raise ParseError(self.current_line, "Syntax error: Unrecognized line format.")
                except ParseError:
                    raise
                except ValueError as e:
                    raise ParseError(self.current_line, str(e))
        
        self._validate_final_state()

    def   _parse_nb_drones(self, line: str) -> None:
        
        if self.nb_drones is not None:
            raise ParseError(self.current_line, "Syntax error: Duplicate definition of 'nb_drones'.")
        try:
            value  = validate_positive_int(line.split()[1].strip())
            self.nb_drones = value
            
        except ValueError as e:
            raise ParseError(self.current_line, str(e))
        
    def _parse_hub(self, line: str, hub_type: str) -> None:

        if self.nb_drones is None:
            raise ValueError("Drones number must be declared before zones")

        if hub_type not in ("normal", "start", "end"):
            raise ValueError("Syntax error: Unrecognized hub prefix.")

        line = line.split(":", 1)[1].strip()
        name_n_coords, metadata = extract_metadata(line)
        name, x, y = parse_hub_parts(name_n_coords)
        if name in self.zones:
            raise ValueError(f"Semantic error: Duplicate zone definition for '{name}'.")
        zone_type = metadata.get("zone", "normal")
        if zone_type not in ("normal", "blocked", "restricted", "priority"):
            raise ValueError(f"Semantic error: Invalid zone type '{zone_type}'. Expected: normal, blocked, restricted, priority.")
        max_drones: int | float = validate_positive_int(metadata.get("max_drones", "1"))
        if hub_type in ("start", "end"):
            max_drones = float("inf")
        self.zones[name] = {
            "x": x,
            "y": y,
            "zone_type": zone_type,
            "color": metadata.get("color", ""),
            "max_drones": max_drones,
            "is_start": hub_type == "start",
            "is_end": hub_type == "end",
        }
        if hub_type == "start":
            if self.start_hub_count >= 1:
                raise ValueError("Semantic error: Multiple 'start_hub' zones defined. Only one is permitted.")
            self.start_hub_name = name
            self.start_hub_count += 1
        elif hub_type == "end":
            if self.end_hub_count >= 1:
                raise ValueError("Semantic error: Multiple 'end_hub' zones defined. Only one is permitted.")
            self.end_hub_name = name
            self.end_hub_count += 1
            
    def _parse_connection(self, line: str) -> None:
        if self.nb_drones is None:
            raise ValueError("Drones number must be declared before zones")
        
        raw_cammand = line.split(":", 1)[1].strip()
        link, cost =  extract_metadata(raw_cammand)
        z1, z2 = split_connection(link)
        if z1 not in self.zones:
            raise ValueError(f"Semantic error: Connection references undefined zone '{z1}'.")
        if z2 not in self.zones:
            raise ValueError(f"Semantic error: Connection references undefined zone '{z2}'.")
        if z1 == z2:
            raise ValueError(f"Semantic error: Self-referencing connections are not permitted (zone '{z1}').")
        if frozenset({z1, z2}) in self.seen_connections:
            raise ValueError(f"Semantic error: Duplicate connection defined between '{z1}' and '{z2}'.")
        max_link_capacity = validate_positive_int(cost.get("max_link_capacity", "1"))
        self.seen_connections.add(frozenset({z1, z2}))
        self.connections.append({
                                "zone1": z1,
                                "zone2": z2,
                                "max_link_capacity": max_link_capacity
        })
        
    def _validate_final_state(self) -> None:
        if self.nb_drones is None:
            raise ParseError(0, "Validation error: Missing required 'nb_drones' definition.")
        if self.start_hub_count != 1:
            raise ParseError(0, f"Validation error: Map must contain exactly one 'start_hub' (found {self.start_hub_count}).")
        if self.end_hub_count != 1:
            raise ParseError(0, f"Validation error: Map must contain exactly one 'end_hub' (found {self.end_hub_count}).")