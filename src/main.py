from src.visualization.graphical import Visualizer
from src.pathfinding.scheduler import Scheduler
from src.pathfinding.yen import k_shortest_paths
from src.model.graph import Graph
from src.parsing.parser import MapParser
import sys
import os

# Add the project root to the python path so imports work correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    if len(sys.argv) != 2:
        print("Usage: python src/main.py <map_file>")
        return

    map_path = sys.argv[1]

    try:
        # 1. Parse the file
        parser = MapParser(map_path)
        parser.parse()

        # 2. Build the model
        graph = Graph(parser)

        # 3. Find paths using Yen's K-Shortest Paths (let's find 3 paths)
        paths = k_shortest_paths(graph, graph.start_hub, graph.end_hub, k=3)

        if not paths:
            print("Error: No paths found from start to end.")
            return

        # 4. Schedule and simulate the movements
        scheduler = Scheduler(graph, paths)
        turns = scheduler.simulate()

        # 5. Output the turn-by-turn simulation (Mandatory for grading)
        valid_turns = 0
        for turn in turns:
            if turn.strip():
                print(turn)
                valid_turns += 1

        print(f"\nTotal turns: {valid_turns}")

        # 6. Launch Graphical Visualizer!
        vis = Visualizer(graph, turns)
        vis.start()

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
