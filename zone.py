class Zone:
    """Represents a location in the map graph."""

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        zone_type: str = "normal",
        color: str = "",
        max_drones: int = 1,
        is_start: bool = False,
        is_end: bool = False,
    ) -> None:
        """Initialize a zone with its properties."""
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.color = color
        self.max_drones = max_drones
        self.is_start = is_start
        self.is_end = is_end

    def __str__(self) -> str:
        """Return a string representation of the zone."""
        return (
            f"<Zone {self.name} ({self.x}, {self.y}) "
            f"type={self.zone_type} cap={self.max_drones}>"
        )
