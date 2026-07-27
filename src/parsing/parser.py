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

    def parse(self) -> None:
        with open(self.filepath, "r") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                self.current_line = line_num
                if not line or line.startswith("#"):
                    continue
                if line.startswith("nb_drones:"):
                    self.nb_drones = int(line.split(":")[1].strip())
                elif line.startswith("start_hub:"):
                    content , details = extract_metadata(line.split(":")[1].strip())
                    name , X , Y = parse_hub_parts(content)
                    if name in self.zones:
                        raise ParseError(self.current_line, f"Duplicate zone name: {name}")
                    self.zones[name] = {"X": X, "Y": Y, "metadata": details}
                
