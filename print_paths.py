from src.parsing.parser import MapParser
from src.model.graph import Graph
from src.pathfinding.yen import k_shortest_paths

parser = MapParser("maps/hard/02_capacity_hell.txt")
parser.parse()
graph = Graph(parser)
paths = k_shortest_paths(graph, graph.start_hub, graph.end_hub, k=6)
for i, (p, c) in enumerate(paths):
    print(f"Path {i+1}: {' -> '.join(p)}")
