from typing import List


class Drone:
    """Represents a drone navigating through the map."""

    def __init__(self, drone_id: int, current_zone: str) -> None:
        """Initialize a new drone with its ID and starting zone."""
        self.drone_id = drone_id
        self.current_zone = current_zone
        self.status = "waiting"
        self.path: List[str] = []
        self.path_index = 0
        self.in_transit = False

    def __str__(self) -> str:
        """Return a string representation of the drone's status."""
        return (
            f"<Drone {self.drone_id} at {self.current_zone} "
            f"(status: {self.status})>"
        )
