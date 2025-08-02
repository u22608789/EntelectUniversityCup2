import numpy as np
from zoo_grid import can_place_resource, place_resource
from collections import Counter, defaultdict
import random

def solve_level(level, resources):
    grid = np.array(level["base_grid"])
    lvl = level["level"]
    avail = level["available_resources"]
    placements = []
    type_counts = Counter()
    total_cost = 0

    # --- Step 1: Compute value list (IF/cost) ---
    value_resources = []
    for rid in avail:
        res = resources[rid]
        IF = res["interest_factor"]
        cost = res["cost"]
        for oi, orient in enumerate(res["orientations"]):
            value = IF / cost if cost else IF
            area = len(orient["cells"])
            value_resources.append((value, rid, oi, IF, cost, area))
    value_resources.sort(reverse=True)  # Highest IF/cost first

    # --- Step 2: Pick 15 resource/orientation pairs for diversity ---
    # Avoid repeats for a resource_id, pick best orientation for each
    best_for_type = {}
    for value, rid, oi, IF, cost, area in value_resources:
        if rid not in best_for_type:
            best_for_type[rid] = (value, rid, oi, IF, cost, area)
        if len(best_for_type) >= 15:
            break
    diverse_types = list(best_for_type.values())

    # Randomize order for round robin (for even fill)
    random.shuffle(diverse_types)
    N = len(diverse_types)

    # --- Step 3: Cluster high-IF resources in a synergy block (center 100x100) ---
    center_start = (grid.shape[0]//2 - 50, grid.shape[1]//2 - 50)
    center_end   = (grid.shape[0]//2 + 50, grid.shape[1]//2 + 50)
    for idx, (value, rid, oi, IF, cost, area) in enumerate(diverse_types[:4]):
        res = resources[rid]
        # Try to fill cluster area with these types
        for r in range(center_start[0], center_end[0]):
            for c in range(center_start[1], center_end[1]):
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

    # --- Step 4: Fill rest of grid round robin (max balance) ---
    height, width = grid.shape
    fill_idx = 0
    rr_idx = 0
    open_cells = [(r, c) for r in range(height) for c in range(width) if grid[r, c] == 1]
    random.shuffle(open_cells)  # For more even fill and less bias

    while fill_idx < len(open_cells):
        r, c = open_cells[fill_idx]
        # Strict round robin: always try to place the next resource type
        for j in range(N):
            k = (rr_idx + j) % N
            value, rid, oi, IF, cost, area = diverse_types[k]
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
                rr_idx = (k + 1) % N  # Move to next in round robin for next cell
                break
        fill_idx += 1

    # --- Step 5: Patch fill with small, cheap types to fill last holes ---
    # Optional: add code to sweep with smallest/cheapest types for coverage

    return {"grid": grid, "placements": placements}
