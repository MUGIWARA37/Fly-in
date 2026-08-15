from scheduler import Scheduler
from dfs import dfs
from graph import Graph
from parser import MapParser
from rich import print
from rich.markup import escape
import sys


def main() -> None:
    """Main entry point to parse, route, and simulate drone movements."""
    if len(sys.argv) != 2:
        print("Usage: python main.py <map_file>")
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
        best_turns = None
        # Try all k values and keep the best (fewest turns)
        max_k = min(10, len(all_paths))
        for k_val in range(1, max_k + 1):
            paths = all_paths[:k_val]
            scheduler = Scheduler(graph, paths)
            try:
                result = scheduler.simulate()
                valid = len([t for t in result if t.strip()])
                if best_turns is None or valid < best_turns:
                    best_turns = valid
                    turns = result
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

        for turn in turns:
            if turn.strip():
                colored_movements = []
                for movement in turn.split(" "):
                    parts = movement.split("-")
                    target_zone = parts[-1]
                    color = graph.get_zone(target_zone).color.lower()

                    safe_movement = escape(movement)
                    if not color:
                        colored_movements.append(safe_movement)
                    elif color == "rainbow":
                        colors = [
                            "red",
                            "yellow",
                            "green",
                            "cyan",
                            "blue",
                            "magenta",
                        ]
                        rainbow_text = ""
                        i = 0
                        while i < len(movement):
                            c = colors[i % len(colors)]
                            rainbow_text += f"[{c}]{movement[i]}[/{c}]"
                            i += 1
                        colored_movements.append(rainbow_text)
                    else:
                        colored_movements.append(
                            f"[{color}]{safe_movement}[/{color}]"
                        )

                print(" ".join(colored_movements))
                valid_turns += 1

        print(f"\nTotal turns: {valid_turns}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
