from typing import List, Tuple
from graph import Graph


def dfs(
    graph: Graph, start: str, end: str
) -> List[Tuple[List[str], float]]:
    """
    Finds all possible simple paths from start to end using DFS.
    Sorts by cost first, then by most priority zones as tiebreaker.
    """
    all_paths: List[Tuple[List[str], float, int]] = []

    def search(
        current: str,
        path: List[str],
        current_cost: float,
        priority_count: int,
    ) -> None:
        if current == end:
            all_paths.append(
                (list(path), current_cost, priority_count)
            )
            return

        for neighbor_zone in graph.get_neighbors(current):
            if neighbor_zone.zone_type == "blocked":
                continue
            neighbor = neighbor_zone.name
            if neighbor not in path:
                cost = graph.get_move_cost(neighbor)
                bonus = (
                    1
                    if neighbor_zone.zone_type == "priority"
                    else 0
                )
                path.append(neighbor)
                search(
                    neighbor,
                    path,
                    current_cost + cost,
                    priority_count + bonus,
                )
                path.pop()

    search(start, [start], 0.0, 0)

    # Sort by cost first, then prefer more priority zones
    all_paths.sort(key=lambda x: (x[1], -x[2]))

    # Return without the priority count
    return [(path, cost) for path, cost, _ in all_paths]
