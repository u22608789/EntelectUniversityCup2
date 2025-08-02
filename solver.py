# solver.py (at top)
import time
from zoo_grid import can_place_resource
from zoo_grid import place_resource
import numpy as np



# def solve_level(level, resources):
#     grid       = np.array(level["base_grid"])
#     lvl        = level["level"]
#     avail      = level["available_resources"]
#     placements = []
#     # pre‐check grid size/ids once
#     # from zoo_grid import check_grid_size, check_allowed_ids
#     # check_grid_size(grid, lvl)
#     # check_allowed_ids(grid, lvl)

#     # build sorted list of (rid, orient_idx, cell_count)
#     items = []
#     for rid in avail:
#         res = resources[rid]
#         for oi, orient in enumerate(res["orientations"]):
#             items.append((rid, oi, len(orient["cells"])))
#     items.sort(key=lambda x: x[2], reverse=True)
    
    
    

#     placed_any = True
#     while placed_any:
#         placed_any = False
#         for rid, oi, _ in items:
#             res = resources[rid]
#             for r in range(grid.shape[0]):
#                 for c in range(grid.shape[1]):
#                     if can_place_resource(grid, res, oi, (r,c), level=lvl):
#                         place_resource     (grid, res, oi, (r,c))
#                         placements.append({"resource_id":rid,
#                                            "rotation":   oi,
#                                            "top":        r,
#                                            "left":       c})
#                         placed_any = True
#         # if in a full sweep nothing got placed, loop will exit

#     return {"grid": grid, "placements": placements}

def solve_level(level, resources):
    grid       = np.array(level["base_grid"])
    lvl        = level["level"]
    avail      = level["available_resources"]
    placements = []

    # Build initial list of (rid, oi, cell_count)
    items = []
    for rid in avail:
        res = resources[rid]
        for oi, orient in enumerate(res["orientations"]):
            items.append((rid, oi, len(orient["cells"])))
    # items.sort(key=lambda x: x[2], reverse=True)  # We'll sort dynamically below

    # Track usage counts for each resource_id
    resource_counts = {rid: 0 for rid in avail}

    for r in range(grid.shape[0]):
        for c in range(grid.shape[1]):
            if grid[r, c] != 1:
                continue  # already filled

            # Sort by least used count, then largest area
            items_sorted = sorted(
                items,
                key=lambda x: (resource_counts[x[0]], -x[2])
            )

            for rid, oi, _ in items_sorted:
                res = resources[rid]
                if can_place_resource(grid, res, oi, (r, c), level=lvl):
                    place_resource(grid, res, oi, (r, c))
                    placements.append({
                        "resource_id": rid,
                        "rotation": oi,
                        "top": r,
                        "left": c
                    })
                    resource_counts[rid] += 1
                    break  # Only one resource per cell

    return {"grid": grid, "placements": placements}
