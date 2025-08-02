# zoo_grid.py

import numpy as np
from utils import chebyshev_dist, in_bounds

ALLOWED_IDS_LEVEL_1 = {1,3,4,6,9,10,11,14,15,20,21}
ALLOWED_IDS_LEVEL_2 = {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22}

def check_grid_size(grid: np.ndarray, level: int):
    expected = (50,50) if level==1 else (100,100)
    if grid.shape != expected:
        raise ValueError(f"Level {level} needs grid {expected}, got {grid.shape}")

def check_allowed_ids(grid: np.ndarray, level: int):
    allowed = ALLOWED_IDS_LEVEL_1 if level==1 else ALLOWED_IDS_LEVEL_2
    invalid = np.setdiff1d(np.unique(grid), list(allowed))
    if invalid.size:
        raise ValueError(f"Found invalid IDs {invalid.tolist()} for Level {level}")

def can_place_resource(grid: np.ndarray,
                       resource: dict,
                       orient_idx: int,
                       top_left: tuple[int,int],
                       level: int=1) -> bool:
    """Bounds, overlap, same‐type spacing (L1) or radius‐5 incompatibility (L2+)."""
    # check_grid_size(grid, level)
    # check_allowed_ids(grid, level)

    cells = resource["orientations"][orient_idx]["cells"]
    rid   = resource["resource_id"]
    occupied = []

    # 1) Bounds & overlap
    for dr,dc in cells:
        r,c = top_left[0]+dr, top_left[1]+dc
        if not in_bounds(grid, r,c): return False
        if grid[r,c] != 1:            return False
        occupied.append((r,c))

    # 2) Level 1: no adjacent same‐type
    if level==1:
        for r,c in occupied:
            for dr in (-1,0,1):
                for dc in (-1,0,1):
                    if dr==0 and dc==0: continue
                    nr,nc = r+dr, c+dc
                    if in_bounds(grid,nr,nc) and grid[nr,nc]==rid:
                        return False
        return True

    # 3) Level 2+: radius‐5 incompatibility
    forbidden = set(resource.get("incompatible_with",[])) | {rid}
    R = 5
    for r,c in occupied:
        for dr in range(-R,R+1):
            for dc in range(-R,R+1):
                if dr==0 and dc==0: continue
                nr,nc = r+dr, c+dc
                if not in_bounds(grid,nr,nc): continue
                other = grid[nr,nc]
                if other in forbidden and (nr,nc) not in occupied:
                    return False
    return True

def place_resource(grid: np.ndarray,
                   resource: dict,
                   orient_idx: int,
                   top_left: tuple[int,int]) -> None:
    """Mutate grid in place."""
    cells = resource["orientations"][orient_idx]["cells"]
    rid   = resource["resource_id"]
    for dr,dc in cells:
        r,c = top_left[0]+dr, top_left[1]+dc
        grid[r,c] = rid

def print_grid(grid: np.ndarray):
    for row in grid:
        print(" ".join(f"{x:2}" for x in row))
