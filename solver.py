import numpy as np
from zoo_grid import can_place_resource, place_resource
from collections import Counter

def solve_level(level, resources):
    grid = np.array(level["base_grid"])
    lvl = level["level"]
    avail = level["available_resources"]
    placements = []
    type_counts = Counter()
    total_cost = 0

    # --- Step 1: Precompute value list (IF/cost) ---
    value_resources = []
    for rid in avail:
        res = resources[rid]
        IF = res["interest_factor"]
        cost = res["cost"]
        for oi, orient in enumerate(res["orientations"]):
            value = IF / cost if cost else IF
            value_resources.append((value, rid, oi, IF, cost))
    value_resources.sort(reverse=True)  # Highest IF/cost first

    # --- Step 2: Pick Top N Resource/Orientation pairs ---
    TOP_N = 6  # You can adjust N (5–8 is a good range)
    top_resources = value_resources[:TOP_N]

    height, width = grid.shape

    # --- Step 3: For each resource, fill as much as possible, round robin style ---
    for _, rid, oi, IF, cost in top_resources:
        res = resources[rid]
        for r in range(height):
            for c in range(width):
                if grid[r, c] != 1:
                    continue
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
    return {"grid": grid, "placements": placements}
