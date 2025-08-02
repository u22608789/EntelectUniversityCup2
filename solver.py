import numpy as np
from zoo_grid import can_place_resource, place_resource
from collections import Counter
import random

def solve_level(level, resources):
    grid = np.array(level["base_grid"])
    lvl = level["level"]
    avail = level["available_resources"]
    placements = []
    type_counts = Counter()
    total_cost = 0

    # Pick ONE best orientation per resource, sorted by IF/cost
    best_types = []
    for rid in avail:
        best = None
        for oi, orient in enumerate(resources[rid]["orientations"]):
            IF = resources[rid]["interest_factor"]
            cost = resources[rid]["cost"]
            area = len(orient["cells"])
            value = (IF * area) / (cost+1)  # +1 to avoid divide by zero
            if not best or value > best[0]:
                best = (value, rid, oi, IF, cost)
        best_types.append(best)
    # Now sort by value
    best_types.sort(reverse=True)

    # Use top 20 for maximum diversity
    top_types = best_types[:20]

    # Randomize open cells for balance
    height, width = grid.shape
    open_cells = [(r, c) for r in range(height) for c in range(width) if grid[r, c] == 1]
    random.shuffle(open_cells)

    idx = 0
    while idx < len(open_cells):
        for value, rid, oi, IF, cost in top_types:
            if idx >= len(open_cells):
                break
            r, c = open_cells[idx]
            if grid[r, c] != 1:
                idx += 1
                continue
            res = resources[rid]
            if can_place_resource(grid, res, oi, (r, c), level=lvl):
                place_resource(grid, res, oi, (r, c))
                placements.append({
                    "resource_id": rid,
                    "rotation": oi,
                    "top": r,
                    "left": c
                })
                type_counts[rid] += 1
                total_cost += cost
            idx += 1

    return {"grid": grid, "placements": placements}
