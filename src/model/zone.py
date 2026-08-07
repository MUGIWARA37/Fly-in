class Zone:
    def __init__(self, name: str, x: int, y: int, zone_type: str = "normal",
                 color: str = "",
                 max_drones: int = 1,
                 is_start: bool = False,
                 is_end: bool = False
                 ) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.color = color
        self.max_drones = max_drones
        self.is_start = is_start
        self.is_end = is_end

    def __str__(self) -> str:
        return f"<Zone '{self.name}' ({self.x}, {self.y}) type={self.zone_type}>"
