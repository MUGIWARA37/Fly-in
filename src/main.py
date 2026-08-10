# mypy: ignore-errors
import sys
import os

# Add the project root to the python path so imports work correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.visualization.graphical import Visualizer  # noqa: E402
from src.pathfinding.scheduler import Scheduler  # noqa: E402
from src.pathfinding.dfs import dfs  # noqa: E402
from src.model.graph import Graph  # noqa: E402
from src.parsing.parser import MapParser  # noqa: E402


def main() -> None:
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

        # 3. Find ALL paths using DFS, and take the top shortest ones
        assert graph.start_hub is not None and graph.end_hub is not None
        all_paths = dfs(graph, graph.start_hub, graph.end_hub)
        if not all_paths:
            print("Error: No paths found from start to end.")
            return

        turns = None
        # Start at k=4 (optimal for 44-turn Impossible Dream) and fallback to
        # avoid deadlocks
        for k_val in range(4, 0, -1):
            paths = all_paths[:k_val] if len(all_paths) >= k_val else all_paths
            scheduler = Scheduler(graph, paths)
            try:
                turns = scheduler.simulate()
                break
            except Exception as e:
                if str(e) == "DEADLOCK DETECTED":
                    continue
                else:
                    raise e

        if turns is None:
            print("Error: Could not find a deadlock-free routing sequence.")
            return

        # 5. Output the turn-by-turn simulation (Mandatory for grading)
        valid_turns = 0
        # Color map for terminal output
        color_map = {
            "red": "\033[91m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "blue": "\033[94m",
            "purple": "\033[95m",
            "cyan": "\033[96m",
            "white": "\033[97m",
            "black": "\033[90m",
            "brown": "\033[33m",
            "orange": "\033[38;5;208m",
            "maroon": "\033[31m",
            "gold": "\033[38;5;220m",
            "darkred": "\033[38;5;88m",
            "violet": "\033[38;5;177m",
            "crimson": "\033[38;5;161m",
            "rainbow": "\033[38;5;196m",  # simplified rainbow
        }
        reset = "\033[0m"

        for turn in turns:
            if turn.strip():
                colored_movements = []
                for movement in turn.split(" "):
                    parts = movement.split("-")
                    target_zone = parts[-1]
                    color = graph.get_zone(target_zone).color
                    color_code = color_map.get(color.lower(), "")
                    colored_movements.append(f"{color_code}{movement}{reset}")
                print(" ".join(colored_movements))
                valid_turns += 1

        print(f"\nTotal turns: {valid_turns}")

        # 6. Launch Graphical Visualizer!
        vis = Visualizer(graph, turns)
        vis.start()

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
