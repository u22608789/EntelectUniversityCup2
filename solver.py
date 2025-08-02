from zoo_grid import can_place_resource, place_resource
import numpy as np

def solve_level(level, resources):
    grid = np.array(level["base_grid"])
    lvl = level["level"]
    avail = level["available_resources"]
    placements = []
    
    # Initialize resource counts
    resource_counts = {rid: 0 for rid in avail}
    
    # Build list of (rid, orient_idx)
    items = [(rid, oi) for rid in avail for oi in range(len(resources[rid]["orientations"]))]
    
    # Single pass over the grid
    for r in range(grid.shape[0]):
        for c in range(grid.shape[1]):
            if grid[r, c] != 1:  # Skip occupied or invalid cells
                continue
            # Find all valid placements at this position
            valid_placements = []
            for rid, oi in items:
                if can_place_resource(grid, resources[rid], oi, (r, c), level=lvl):
                    valid_placements.append((rid, oi))
            if valid_placements:
                # Choose resource with minimum count for balance
                min_count = min(resource_counts[rid] for rid, _ in valid_placements)
                candidates = [(rid, oi) for rid, oi in valid_placements if resource_counts[rid] == min_count]
                # Break ties by smallest resource ID
                rid, oi = min(candidates, key=lambda x: x[0])
                place_resource(grid, resources[rid], oi, (r, c))
                placements.append({"resource_id": rid, "rotation": oi, "top": r, "left": c})
                resource_counts[rid] += 1
    
    return {"grid": grid, "placements": placements}