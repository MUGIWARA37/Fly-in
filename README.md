_This project has been created as part of the 42 curriculum by rhlou._

# Fly-In: Drone Routing and Visualization

## Description
Fly-In is a comprehensive drone pathfinding and simulation engine. The primary goal of the project is to parse complex network maps (representing logistical hubs, waypoints, and constrained zones) and automatically route a swarm of drones from a starting hub to an ending hub in the absolute minimum number of turns. 

The project successfully handles multiple constraints, including:
- **Restricted Zones**: Require 2 turns of transit time.
- **Priority Zones**: Preferred fast-lanes.
- **Blocked Zones**: Inaccessible areas.
- **Capacity Constraints**: Strict limits on how many drones can occupy a zone or connection at any given time.

The project natively solves all provided maps, successfully conquering the quasi-unsolvable "The Impossible Dream" map in exactly 45 turns, matching the challenge record.

## Instructions

The project uses a `Makefile` to handle all compilation, linting, and execution.

### Prerequisites
- Python 3.11+
- `tkinter` (Standard library, required for GUI)

### Commands
- `make install`: Installs necessary dependencies (`flake8`, `mypy`).
- `make run`: Executes the simulation on `maps/hard/03_ultimate_challenge.txt`.
- `make debug`: Runs the simulation with Python's built-in `pdb` debugger.
- `make clean`: Removes `__pycache__` and `.mypy_cache` temporary files.
- `make lint`: Runs `flake8` and `mypy` against the `src/` directory.

To run a specific map manually from the terminal:
```bash
python3 src/main.py maps/challenger/01_the_impossible_dream.txt
```

## Resources
During the development of this project, the following resources were leveraged:
- **Breadth-First Search (BFS)**: Documentation on exhaustive pathfinding and state-space exploration.
- **Python `tkinter` Reference**: Used to build the graphical interface and the non-blocking event loop using `root.after()`.
- **AI Usage (Antigravity Model)**: AI was utilized to act as a pair-programming partner. Specifically, it was used to write boilerplate code, design the custom mathematical formulas for the GUI drone animations (rotational vectors using `math.atan2` and cubic acceleration `ease_in_out_cubic`), and debug complex bottleneck deadlocks during the capacity-constrained routing phases.

## Algorithm Choices
The core routing logic relies on a two-step process:
1. **Breadth-First Search (BFS) Path Generation**: Instead of relying on traditional Dijkstra or Yen's K-Shortest Paths (which struggled with the bidirectional capacity bottlenecks), we implemented an exhaustive BFS search in `src/pathfinding/bfs.py`. This explores all possible simple paths through the graph, inherently avoiding cycles and bypassing blocked nodes entirely. The algorithm computes the exact cost of each generated path based on the zone configurations (e.g., restricted zones cost 2.0). 
2. **Cost-Based Sorting and Top-K Selection**: The BFS generator sorts every single valid path by its final cost. The system extracts the top 3 absolute shortest paths and feeds them into the `Scheduler` to distribute the drone swarm load, entirely avoiding capacity-induced gridlocks.

## Visual Representation
A graphical visualizer is provided in `src/visualization/graphical.py` to allow real-time observation of the routing algorithm.
- **Aesthetic**: The UI utilizes an elegant "Midnight Slate & Emerald" color palette, creating a professional, modern terminal dashboard feel.
- **UX Features**: It features dynamic resizing based on the node coordinates (`min_x`, `max_x`), ensuring that the graph automatically centers itself perfectly regardless of the map size.
- **Animations**: It employs custom cubic easing functions to accelerate drones out of nodes, and trigonometric calculations to accurately rotate the dart-shaped drones to face their exact movement vector, vastly improving the clarity of the swarm's trajectory.

## Example Input and Output

### Input Map Example (`map.txt`)
```text
nb_drones: 2
start_hub: start 0 0 [color=green]
hub: A 1 0 [color=blue max_drones=1]
end_hub: end 2 0 [color=green]
connection: start-A
connection: A-end
```

### Expected Execution Output
```bash
$ python3 src/main.py map.txt
D1-start-A
D1-A D2-start-A
D1-A-end D2-A
D1-end D2-A-end
D2-end

Total turns: 5
```
