from .zone import Zone


class Connection:
    def __init__(self, zone_a: Zone, zone_b: Zone,
                 max_link_capacity: int = 1) -> None:
        self.zone_a = zone_a
        self.zone_b = zone_b
        self.max_link_capacity = max_link_capacity

    def __str__(self) -> str:
        return f"<Connection {self.zone_a.name} <-> {self.zone_b.name} (cap: {self.max_link_capacity})>"
