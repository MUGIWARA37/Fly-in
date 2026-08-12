from typing import Dict, List
from tokens import (
    validate_positive_int,
    extract_metadata,
    split_connection,
)
from exceptions import ParseError


class MapParser:
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.nb_drones: int | None = None
        self.start_hub_count: int = 0
        self.end_hub_count: int = 0
        from typing import Any

        self.zones: Dict[str, Dict[str, Any]] = {}
        self.connections: List[Dict[str, Any]] = []
        self.current_line: int = 0
        self.start_hub_name: str | None = None
        self.end_hub_name: str | None = None
        self.seen_connections: set[frozenset[str]] = set()

    def parse(self) -> None:
        with open(self.filepath, "r") as f:
            for line_num, line in enumerate(f, start=1):
                self.current_line = line_num
                line = line.split("#", 1)[0].strip()
                if not line:
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
                        raise ParseError(
                            self.current_line,
                            "Syntax error: Unrecognized line format."
                        )
                except ValueError as e:
                    raise ParseError(self.current_line, str(e))

        self._validate_final_state()

    def _parse_nb_drones(self, line: str) -> None:

        if self.nb_drones is not None:
            raise ParseError(
                self.current_line,
                "Syntax error: Duplicate definition of 'nb_drones'."
            )
        try:
            value = validate_positive_int(line.split()[1].strip())
            self.nb_drones = value

        except ValueError as e:
            raise ParseError(self.current_line, str(e))

    def _parse_hub(self, line: str, hub_type: str) -> None:

        if self.nb_drones is None:
            raise ValueError("Drones number must be declared before zones")

        if hub_type not in ("normal", "start", "end"):
            raise ValueError("Syntax error: Unrecognized hub prefix.")

        line = line.split(":", 1)[1].strip()
        parts = line.split(maxsplit=3)
        if len(parts) < 3:
            raise ValueError("Syntax error: Missing name or coordinates")

        name = parts[0]
        try:
            x, y = int(parts[1]), int(parts[2])
        except ValueError:
            raise ValueError("Syntax error: Invalid integer for coordinates")

        metadata: Dict[str, str] = {}
        if len(parts) == 4:
            meta_str = parts[3].strip()
            if not meta_str.startswith("[") or not meta_str.endswith("]"):
                raise ValueError(
                    f"Syntax error: Invalid metadata format or trailing characters. Expected '[...]', got '{meta_str}'")
            _, metadata = extract_metadata(meta_str)
        if name in self.zones:
            raise ValueError(
                f"Semantic error: Duplicate zone definition for '{name}'."
            )

        for z_name, z_data in self.zones.items():
            if z_data["x"] == x and z_data["y"] == y:
                raise ValueError(
                    f"Semantic error: Coordinates ({x}, {y}) for zone '{name}' are already used by zone '{z_name}'."
                )
        zone_type = metadata.get("zone", "normal")
        if zone_type not in ("normal", "blocked", "restricted", "priority"):
            raise ValueError(
                f"Semantic error: Invalid zone type '{zone_type}'. Expected: normal, blocked, restricted, priority."
            )

        if hub_type in ("start", "end") and zone_type == "blocked":
            raise ValueError(
                f"Semantic error: The {hub_type}_hub cannot be a blocked zone."
            )
        max_drones: int = validate_positive_int(
            metadata.get("max_drones", "1")
        )
        if hub_type in ("start", "end"):
            max_drones = 999999999
        color = metadata.get("color", "").lower()
        if color:
            from rich.style import Style
            from rich.errors import StyleSyntaxError

            # Map custom legacy colors from the old ANSI map to exact hex codes
            # for rich
            legacy_map = {
                "brown": "#8B4513",
                "orange": "#FFA500",
                "maroon": "#800000",
                "gold": "#FFD700",
                "darkred": "#8B0000",
                "violet": "#EE82EE",
                "crimson": "#DC143C",
                "purple": "#7603B0",
                "lime": "#00FF00",
                "rainbow": "magenta",
            }
            color = legacy_map.get(color, color)

            try:
                Style.parse(color)
            except StyleSyntaxError:
                original = metadata.get("color", "")
                raise ValueError(
                    f"Semantic error: Unsupported rich color '{original}' for zone '{name}'"
                )

        self.zones[name] = {
            "x": x,
            "y": y,
            "zone_type": zone_type,
            "color": color,
            "max_drones": max_drones,
            "is_start": hub_type == "start",
            "is_end": hub_type == "end",
        }
        if hub_type == "start":
            if self.start_hub_count >= 1:
                raise ValueError(
                    "Semantic error: Multiple 'start_hub' zones defined. Only one is permitted."
                )
            self.start_hub_name = name
            self.start_hub_count += 1
        elif hub_type == "end":
            if self.end_hub_count >= 1:
                raise ValueError(
                    "Semantic error: Multiple 'end_hub' zones defined. Only one is permitted."
                )
            self.end_hub_name = name
            self.end_hub_count += 1

    def _parse_connection(self, line: str) -> None:
        if self.nb_drones is None:
            raise ValueError("Drones number must be declared before zones")

        raw_cammand = line.split(":", 1)[1].strip()
        parts = raw_cammand.split(maxsplit=1)
        if len(parts) < 1:
            raise ValueError("Syntax error: Missing connection data")

        link = parts[0]
        cost: Dict[str, str] = {}
        if len(parts) == 2:
            meta_str = parts[1].strip()
            if not meta_str.startswith("[") or not meta_str.endswith("]"):
                raise ValueError(
                    f"Syntax error: Invalid metadata format or trailing characters. Expected '[...]', got '{meta_str}'")
            _, cost = extract_metadata(meta_str)
        z1, z2 = split_connection(link)
        if z1 not in self.zones:
            raise ValueError(
                f"Semantic error: Connection references undefined zone '{z1}'."
            )
        if z2 not in self.zones:
            raise ValueError(
                f"Semantic error: Connection references undefined zone '{z2}'."
            )
        if z1 == z2:
            raise ValueError(
                f"Semantic error: Self-referencing connections are not permitted (zone '{z1}')."
            )
        if frozenset({z1, z2}) in self.seen_connections:
            raise ValueError(
                f"Semantic error: Duplicate connection defined between '{z1}' and '{z2}'."
            )
        max_link_capacity = validate_positive_int(
            cost.get("max_link_capacity", "1")
        )
        self.seen_connections.add(frozenset({z1, z2}))
        self.connections.append(
            {"zone1": z1, "zone2": z2, "max_link_capacity": max_link_capacity}
        )

    def _validate_final_state(self) -> None:
        if self.nb_drones is None:
            raise ParseError(
                0, "Validation error: Missing required 'nb_drones' definition."
            )
        if self.start_hub_count != 1:
            raise ParseError(
                0,
                f"Validation error: Map must contain exactly one 'start_hub' (found {self.start_hub_count}).",
            )
        if self.end_hub_count != 1:
            raise ParseError(
                0,
                f"Validation error: Map must contain exactly one 'end_hub' (found {self.end_hub_count}).",
            )
