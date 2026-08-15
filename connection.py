from zone import Zone


class Connection:
    """Represents a link between two zones with a capacity limit."""

    def __init__(
        self, zone_a: Zone, zone_b: Zone, max_link_capacity: int = 1
    ) -> None:
        """Initialize a connection between two zones."""
        self.zone_a = zone_a
        self.zone_b = zone_b
        self.max_link_capacity = max_link_capacity

    def __str__(self) -> str:
        """Return a string representation of the connection."""
        return (
            f"<Connection {self.zone_a.name} <-> {self.zone_b.name} "
            f"(cap: {self.max_link_capacity})>"
        )
