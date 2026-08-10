from typing import List, Tuple
from src.model.graph import Graph


def dfs(graph: Graph, start: str, end: str) -> List[Tuple[List[str], float]]:
    """
    Finds all possible simple paths from start to end using DFS.
    Calculates the cost recursively to save operations and sorts by cost.
    """
    all_paths = []

    def dfs(current: str, path: List[str], current_cost: float) -> None:
        if current == end:
            all_paths.append((list(path), current_cost))
            return

        for neighbor_zone in graph.get_neighbors(current):
            if neighbor_zone.zone_type == "blocked":
                continue
            neighbor = neighbor_zone.name
            if neighbor not in path:
                cost = graph.get_move_cost(neighbor)
                path.append(neighbor)
                dfs(neighbor, path, current_cost + cost)
                path.pop()

    dfs(start, [start], 0.0)
    all_paths.sort(key=lambda x: x[1])
    return all_paths
