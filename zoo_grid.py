# zoo_grid.py

import numpy as np
from utils import chebyshev_dist, in_bounds

# ─── CONFIG ────────────────────────────────────────────────────
# Set this to 1 or 2 to choose which placement rules to enforce.
DEFAULT_LEVEL = 2
# ────────────────────────────────────────────────────────────────

# Allowed resource IDs per level
ALLOWED_IDS = {
    1: {1, 3, 4, 6, 9, 10, 11, 14, 15, 20, 21},
    2: {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22},
}

def check_grid_size(grid: np.ndarray, level: int = None):
    """Raise if grid.shape ≠ (50,50) for L1 or (100,100) for L2+."""
    lvl = level or DEFAULT_LEVEL
    expected = (50, 50) if lvl == 1 else (100, 100)
    if grid.shape != expected:
        raise ValueError(f"Level {lvl} grid must be {expected}, got {grid.shape}")

def check_allowed_ids(grid: np.ndarray, level: int = None):
    """Raise if any cell contains an ID not permitted in this level."""
    lvl = level or DEFAULT_LEVEL
    allowed = ALLOWED_IDS[lvl]
    invalid = np.setdiff1d(np.unique(grid), list(allowed))
    if invalid.size:
        raise ValueError(f"Invalid IDs {invalid.tolist()} for Level {lvl}")

def can_place_resource(grid: np.ndarray,
                       resource: dict,
                       orient_idx: int,
                       top_left: tuple[int,int],
                       level: int = None) -> bool:
    """
    Returns True if `resource` at orientation `orient_idx` can go at `top_left`.
    Enforces:
      - bounds & no‐overlap on pathways (cells==1)
      - Level 1: no adjacent same‐type
      - Level 2: no incompatible within Chebyshev radius=5
    """
    lvl = level or DEFAULT_LEVEL
    cells = resource["orientations"][orient_idx]["cells"]
    rid   = resource["resource_id"]

    # 1) Bounds & overlap
    for dr, dc in cells:
        r, c = top_left[0] + dr, top_left[1] + dc
        if not in_bounds(grid, r, c):
            return False
        if grid[r, c] != 1:
            return False

    # 2) Level 1: forbid any same‐type in the 8‐neighborhood
    if lvl == 1:
        for dr, dc in cells:
            r, c = top_left[0] + dr, top_left[1] + dc
            for drow in (-1, 0, 1):
                for dcol in (-1, 0, 1):
                    if drow == 0 and dcol == 0:
                        continue
                    nr, nc = r + drow, c + dcol
                    if in_bounds(grid, nr, nc) and grid[nr, nc] == rid:
                        return False
        return True

    # 3) Level 2+: forbid any incompatible resource within Chebyshev R=5
    forbidden = set(resource.get("incompatible_with", []))
    R = 5
    for dr, dc in cells:
        r, c = top_left[0] + dr, top_left[1] + dc
        for drow in range(-R, R+1):
            for dcol in range(-R, R+1):
                if drow == 0 and dcol == 0:
                    continue
                nr, nc = r + drow, c + dcol
                if not in_bounds(grid, nr, nc):
                    continue
                if grid[nr, nc] in forbidden:
                    return False
    return True

def place_resource(grid: np.ndarray,
                   resource: dict,
                   orient_idx: int,
                   top_left: tuple[int,int]) -> None:
    """Mutate `grid` by stamping the resource’s ID into each of its cells."""
    cells = resource["orientations"][orient_idx]["cells"]
    rid   = resource["resource_id"]
    for dr, dc in cells:
        r, c = top_left[0] + dr, top_left[1] + dc
        grid[r, c] = rid

def print_grid(grid: np.ndarray) -> None:
    """Simple ASCII dump of the grid for debugging."""
    for row in grid:
        print(" ".join(f"{x:2}" for x in row))
