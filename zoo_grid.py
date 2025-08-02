# zoo_grid.py

import json
import numpy as np
from utils import chebyshev_dist, in_bounds

# ─── CONFIGURATION ─────────────────────────────────────────────
# Change this to 1, 2 or 3 to pick your rule set
DEFAULT_LEVEL = 3

# Path to your resources.json
RESOURCES_FILE = "resources.json"
# ────────────────────────────────────────────────────────────────

# Load resource definitions once at import time
with open(RESOURCES_FILE, 'r') as f:
    _RESOURCES = json.load(f)["resources"]

# Map id → resource dict for quick lookup
RESOURCE_MAP = {r["resource_id"]: r for r in _RESOURCES}

# Allowed resource IDs by level
ALLOWED_IDS = {
    1: {1, 3, 4, 6, 9, 10, 11, 14, 15, 20, 21},
    2: {r["resource_id"] for r in _RESOURCES if r["resource_id"] <= 22},
    3: {r["resource_id"] for r in _RESOURCES},  # all resources available
}


def check_grid_size(grid: np.ndarray, level: int = None):
    """Ensure grid shape matches the chosen level."""
    lvl = level or DEFAULT_LEVEL
    expected = {1: (50, 50), 2: (100, 100), 3: (300, 300)}[lvl]
    if grid.shape != expected:
        raise ValueError(f"Level {lvl} needs grid size {expected}, got {grid.shape}")


def check_allowed_ids(grid: np.ndarray, level: int = None):
    """Raise if grid contains any ID not allowed at this level."""
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
    Can we stamp `resource` at orientation `orient_idx` into `grid` at `top_left`?
    Enforces:
      - bounds & no‐overlap on pathways (cells==1)
      - L1: no adjacent same‐type in 8‐neighborhood
      - L2+: no incompatible within Chebyshev radius=5
    """
    lvl = level or DEFAULT_LEVEL
    cells = resource["orientations"][orient_idx]["cells"]
    rid   = resource["resource_id"]

    # 1) Bounds & overlap
    for dr, dc in cells:
        r, c = top_left[0] + dr, top_left[1] + dc
        if not in_bounds(grid, r, c) or grid[r, c] != 1:
            return False

    # 2) Level 1 rule: no identical neighbor
    if lvl == 1:
        for dr, dc in cells:
            r, c = top_left[0] + dr, top_left[1] + dc
            for drow in (-1, 0, 1):
                for dcol in (-1, 0, 1):
                    if drow == dcol == 0:
                        continue
                    nr, nc = r + drow, c + dcol
                    if in_bounds(grid, nr, nc) and grid[nr, nc] == rid:
                        return False
        return True

    # 3) Level 2+ rule: incompatible within radius 5
    forbidden = set(resource.get("incompatible_with", []))
    R = 5
    for dr, dc in cells:
        r, c = top_left[0] + dr, top_left[1] + dc
        for drow in range(-R, R+1):
            for dcol in range(-R, R+1):
                if drow == dcol == 0:
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
                   top_left: tuple[int,int],
                   record: list = None) -> None:
    """
    Stamp `resource` into `grid`.  
    If you pass a `record` list it will append a dict
      { "resource": resource, "orient_idx": orient_idx, "top_left": top_left }
    so you can later compute scoring for Level 3.
    """
    cells = resource["orientations"][orient_idx]["cells"]
    rid   = resource["resource_id"]
    for dr, dc in cells:
        r, c = top_left[0] + dr, top_left[1] + dc
        grid[r, c] = rid

    if record is not None:
        record.append({
            "resource": resource,
            "orient_idx": orient_idx,
            "top_left": top_left
        })


def print_grid(grid: np.ndarray):
    """ASCII‐dump for quick debugging."""
    for row in grid:
        print(" ".join(f"{x:2}" for x in row))


# ─── Level 3 Scoring ────────────────────────────────────────────

def _get_placement_cells(placement: dict) -> set[tuple[int,int]]:
    """Return the set of absolute grid‐cells occupied by one placement."""
    res, ori, tl = placement["resource"], placement["orient_idx"], placement["top_left"]
    return {
        (tl[0] + dr, tl[1] + dc)
        for dr, dc in res["orientations"][ori]["cells"]
    }


def compute_level3_score(grid: np.ndarray,
                         placements: list[dict]) -> float:
    """
    Level 3 gross score = (TotalInterestScore × UtilizedArea × BalanceMultiplier) / 10000

    - TotalInterestScore = Σ [ interest_factor
                              + 0.1 × Σ(neighbor.interest_factor)
                            ] over all placements
      where “neighbor” is any other placement within Chebyshev distance ≤ 10.

    - UtilizedArea = count of grid cells ≠ 1
    - BalanceMultiplier = same as Level 1/2 (must be computed elsewhere)
    """
    # 1) build cell‐sets for fast distance checks
    cell_sets = [ _get_placement_cells(p) for p in placements ]
    interest_score = 0.0

    for i, p in enumerate(placements):
        base_if = p["resource"]["interest_factor"]
        boost = 0.0
        for j, q in enumerate(placements):
            if i == j:
                continue
            # check minimal Chebyshev distance between any cell in i & j
            near = False
            for (r1, c1) in cell_sets[i]:
                # early‐exit inner loop
                if any(
                    max(abs(r1 - r2), abs(c1 - c2)) <= 10
                    for (r2, c2) in cell_sets[j]
                ):
                    near = True
                    break
                if near:
                    break
            if near:
                boost += q["resource"]["interest_factor"] * 0.10

        interest_score += (base_if + boost)

    # 2) utilized area
    utilized_area = int(np.count_nonzero(grid != 1))

    # 3) resource balance multiplier
    #    (reuse your existing function from L1/L2)
    from utils import compute_balance_multiplier
    balance_mul = compute_balance_multiplier(grid)

    # 4) final gross score
    gross = (interest_score * utilized_area * balance_mul) / 10_000
    return gross


def compute_score(grid: np.ndarray,
                  placements: list[dict],
                  level: int = None) -> float:
    """Dispatch to the right scoring function for the chosen level."""
    lvl = level or DEFAULT_LEVEL
    if lvl == 3:
        return compute_level3_score(grid, placements)
    else:
        raise NotImplementedError(f"Scoring for Level {lvl} is not in this module")
