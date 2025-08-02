# the main algorithm

# solver.py

from zoo_grid import ZooGrid
from typing import Dict, Any

def solve_level(level: Dict[str, Any],
                resources: Dict[int, Any]) -> ZooGrid:
    """
    Parses level dict and resource catalog, returns
    a ZooGrid with placements performed.
    """
    engine = ZooGrid(level["base_grid"], resources)
    engine.fill_greedy(level["available_resources"])
    return engine
