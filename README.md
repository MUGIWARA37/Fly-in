_This project has been created as part of the 42 curriculum by rhlou._

# Fly-In: Drone Routing and Simulation

## Description
Fly-In is a comprehensive drone pathfinding and simulation engine. The primary goal of the project is to parse complex network maps (representing logistical hubs, waypoints, and constrained zones) and automatically route a swarm of drones from a starting hub to an ending hub in the absolute minimum number of turns. 

The project successfully handles multiple constraints, including:
- **Restricted Zones**: Require 2 turns of transit time.
- **Priority Zones**: Preferred fast-lanes.
- **Blocked Zones**: Inaccessible areas.
- **Capacity Constraints**: Strict limits on how many drones can occupy a zone or connection at any given time.

The project natively solves all provided maps, successfully conquering the quasi-unsolvable "The Impossible Dream" map in **43 turns**, beating the challenge record of 45 turns.

## Instructions

The project uses a `Makefile` to handle all compilation, linting, and execution. The project utilizes `uv` for lightning-fast virtual environment management.

### Prerequisites
- Python 3.10+
- `uv` package manager

### Commands
- `make install`: Sets up the virtual environment and installs necessary dependencies (`flake8`, `mypy`, `rich`).
- `make run`: Executes the simulation on `maps/challenger/01_the_impossible_dream.txt`.
- `make debug`: Runs the simulation with Python's built-in `pdb` debugger.
- `make clean`: Removes `__pycache__` and `.mypy_cache` temporary files.
- `make lint`: Runs `flake8` and `mypy` against the Python files.
- `make lint-strict`: Runs strict linting validations.

To run a specific map manually from the terminal:
```bash
uv run python3 main.py maps/challenger/01_the_impossible_dream.txt
```

## Resources
During the development of this project, the following resources were leveraged:
- **Depth-First Search (DFS)**: Documentation on exhaustive pathfinding and state-space exploration.
- **Python `rich` Reference**: Used to build the vibrant, dynamically colored terminal output.
- **AI Usage (Antigravity Model)**: AI was utilized to act as a pair-programming partner. Specifically, it was used as an explainer and guide to brainstorm the recursive DFS backtracking logic, understand strict metadata parsing concepts, and design the optimal multi-path k-selection algorithm to bypass severe capacity bottlenecks.

## Algorithm Choices
The core routing logic relies on a two-step process:
1. **Recursive Depth-First Search (DFS) Path Generation**: We implemented an exhaustive, memory-efficient DFS search in `dfs.py`. This explores all possible simple paths through the graph, inherently avoiding cycles and bypassing blocked nodes entirely. The algorithm computes the exact cost of each generated path based on the zone configurations (e.g., restricted zones cost 2.0). 
2. **Cost-Based Sorting and Optimal K-Selection**: The DFS generator sorts every single valid path by its final cost. The `Scheduler` evaluates all possible top-k path combinations (from k=1 to k=10) by simulating the drone swarm load across them. It then statically selects the specific subset of paths that guarantees the lowest total turn count, flawlessly bypassing capacity-induced gridlocks without deadlocking.

## Visual Representation
The project outputs a real-time turn-by-turn simulation directly to the terminal.
- **Aesthetic**: The output utilizes the `rich` library to inject dynamic colors into the terminal. 
- **Dynamic Metadata Parsing**: The parser dynamically reads `[color=...]` metadata tags attached to zones and translates them into corresponding hex codes or standard terminal colors. Unknown or invalid colors immediately trigger a strict-parsing validation error before the engine even boots.

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
$ uv run python3 main.py map.txt
D1-A
D1-end D2-A
D2-end

Total turns: 3
```
