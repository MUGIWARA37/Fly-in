from typing import List, Tuple
from src.model.graph import Graph
from .dijkstra import dijkstra


def k_shortest_paths(graph: Graph, start: str, end: str,
                     k: int) -> List[Tuple[List[str], float]]:
    paths = [dijkstra(graph, start, end)]
    candidates = []

    for i in range(1, k):
        last_path = paths[i - 1][0]

        for indx in range(len(last_path) - 1):
            spr_node = last_path[indx]
            root_path = last_path[:indx]

            blocked = []
            for path, _ in paths:
                if path[:indx + 1] == last_path[:indx + 1]:
                    blocked.append((path[indx], path[indx + 1]))

            try:
                spr_path, spr_cost = dijkstra(
                    graph, spr_node, end, blocked, root_path)
                total_path = root_path + spr_path
                root_cost = sum(
                    graph.get_move_cost(
                        root_path[j]) for j in range(
                        1, len(root_path)))
                total_cost = root_cost + spr_cost
                candidates.append((total_path, total_cost))
            except ValueError:
                continue

        if not candidates:
            break

        candidates.sort(key=lambda x: x[1])
        paths.append(candidates.pop(0))

    return paths
