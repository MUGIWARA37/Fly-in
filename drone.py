from typing import List


class Drone:
    def __init__(self, drone_id: int, current_zone: str) -> None:
        self.drone_id = drone_id
        self.current_zone = current_zone
        self.status = "waiting"
        self.path: List[str] = []
        self.path_index = 0
        self.in_transit = False

    def __str__(self) -> str:
        return (
            f"<Drone {self.drone_id} at {self.current_zone} "
            f"(status: {self.status})>"
        )
