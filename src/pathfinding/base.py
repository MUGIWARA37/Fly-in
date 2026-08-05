from typing import Dict, List, Optional, Tuple
from src.model.graph import Graph


def dijkstra(graph: Graph, start: str, end: str, blocked_edges: Optional[List[Tuple[str, str]]] = None) -> Tuple[List[str], float]:
    dist, prev, visited = {start: 0.0}, {start: None}, set()
    path = []
    if blocked_edges is None:
        blocked_edges = []
    blocked_set = set()
    for a, b in blocked_edges:
        blocked_set.add(frozenset({a, b}))
    
    while True:
        current = None
        current_dist = float("inf")
    
        for zone_name, d in dist.items():
            if zone_name not in visited and d < current_dist:
                current = zone_name
                current_dist = d
        if not current:
            raise ValueError("No path found")
        if current == end:
            node = end
            while node is not None:
                path.insert(0, node)
                node = prev[node]
            return (path, current_dist)

        
        visited.add(current)
        for neighbor in graph.get_neighbors(current):
            if frozenset({current, neighbor.name}) in blocked_set or neighbor.zone_type == "blocked":
                continue
            new_dist = current_dist + graph.get_move_cost(neighbor.name)
            if neighbor.name not in dist or new_dist < dist[neighbor.name]:
                dist[neighbor.name] = new_dist
                prev[neighbor.name] = current
        
