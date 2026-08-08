from typing import List, Tuple
from src.model.graph import Graph

def find_all_paths_bfs(graph: Graph, start: str, end: str) -> List[Tuple[List[str], float]]:
    """
    Finds all possible simple paths from start to end using BFS.
    Calculates the cost of each path and sorts them from lowest to highest cost.
    """
    queue = [[start]]
    all_paths = []
    
    while queue:
        path = queue.pop(0)
        node = path[-1]
        
        if node == end:
            all_paths.append(path)
            continue
            
        for neighbor_zone in graph.get_neighbors(node):
            if neighbor_zone.zone_type == "blocked":
                continue
            neighbor = neighbor_zone.name
            if neighbor not in path:
                new_path = list(path)
                new_path.append(neighbor)
                queue.append(new_path)
                
    # Calculate costs for all found paths
    paths_with_costs = []
    for path in all_paths:
        cost = 0.0
        for i in range(1, len(path)):
            cost += graph.get_move_cost(path[i])
        paths_with_costs.append((path, cost))
        
    # Sort the paths by their calculated cost (lowest first)
    paths_with_costs.sort(key=lambda x: x[1])
    
    return paths_with_costs
