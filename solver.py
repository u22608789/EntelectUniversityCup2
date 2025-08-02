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

    # 1. Prepare best orientation per resource, sorted by IF/cost
    best_types = []
    for rid in avail:
        best = None
        for oi, orient in enumerate(resources[rid]["orientations"]):
            IF = resources[rid]["interest_factor"]
            cost = resources[rid]["cost"]
            area = len(orient["cells"])
            value = (IF * area) / (cost + 1)
            if not best or value > best[0]:
                best = (value, rid, oi, IF, cost)
        best_types.append(best)
    best_types.sort(reverse=True)

    # 2. Main fill: first 20 for coverage and diversity
    top_types_1 = best_types[:20]
    top_types_2 = best_types[20:40]  # Next best
    top_types_3 = best_types[40:60]  # Next next best

    height, width = grid.shape

    # Pass 1
    for value, rid, oi, IF, cost in top_types_1:
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

    # Pass 2 (more types, patch gaps)
    for value, rid, oi, IF, cost in top_types_2:
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

    # Pass 3 (fill smallest holes with even more types)
    for value, rid, oi, IF, cost in top_types_3:
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
