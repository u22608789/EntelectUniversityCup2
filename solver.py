# solver.py (at top)
import time
from zoo_grid import can_place_resource
from zoo_grid import place_resource
import numpy as np
import random
from utils import score_level1
from collections import Counter
from utils import in_bounds, simpsons_index




def score_level2(placements, resources, grid):
    area = 0
    for p in placements:
        orient = next(o for o in resources[p["resource_id"]]["orientations"] if o["rotation"]==p["rotation"])
        area += len(orient["cells"])
    cnt = Counter(p["resource_id"] for p in placements)
    S   = len(cnt)
    D   = simpsons_index(list(cnt.values()))
    M   = (S + 1/D)/2

    # Count compatibility violations
    violations = 0
    for p in placements:
        rid = p["resource_id"]
        orient = next(o for o in resources[rid]["orientations"] if o["rotation"]==p["rotation"])
        forbidden = set(resources[rid].get("incompatible_with", [])) | {rid}
        R = 5
        top, left = p["top"], p["left"]
        for dr, dc in orient["cells"]:
            r, c = top+dr, left+dc
            for ddr in range(-R, R+1):
                for ddc in range(-R, R+1):
                    nr, nc = r+ddr, c+ddc
                    if not in_bounds(grid, nr, nc): continue
                    other = grid[nr, nc]
                    if (ddr!=0 or ddc!=0) and other in forbidden and other != rid:
                        violations += 1

    violations = violations // 2

    final_score = area*M - violations*1000  
    return {"area": area, "unique_types": S, "simpson_D":D, "multiplier":M, "violations": violations, "final_score": final_score}


def solve_level(level, resources, n_trials=10):
    best_score = -float("inf")
    best_result = None

    for trial in range(n_trials):
        random.seed(trial)
        grid = np.array(level["base_grid"])
        lvl = level["level"]
        avail = level["available_resources"]
        placements = []
        resource_counts = {rid: 0 for rid in avail}

        items = []
        for rid in avail:
            res = resources[rid]
            for oi, orient in enumerate(res["orientations"]):
                items.append((rid, oi, len(orient["cells"])))
        items.sort(key=lambda x: -x[2])

        for rid, oi, area in items:
            coords = [(r, c) for r in range(grid.shape[0]) for c in range(grid.shape[1])]
            random.shuffle(coords)
            placed = False
            for r, c in coords:
                if grid[r, c] != 1:
                    continue
                if can_place_resource(grid, resources[rid], oi, (r, c), level=lvl):
                    place_resource(grid, resources[rid], oi, (r, c))
                    placements.append({
                        "resource_id": rid,
                        "rotation": oi,
                        "top": r,
                        "left": c
                    })
                    resource_counts[rid] += 1
                    placed = True
                    break  

        stats = score_level2(placements, resources, grid)
        if stats["final_score"] > best_score:
            best_score = stats["final_score"]
            best_result = {"grid": grid, "placements": placements}

    if best_result is None:
        grid = np.array(level["base_grid"])
        return {"grid": grid, "placements": []}
    return best_result

