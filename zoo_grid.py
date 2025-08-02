import json
import random
import numpy as np
from collections import Counter
from utils import in_bounds

# Load resources
with open('resources.json', 'r') as f:
    resources_data = json.load(f)['resources']
resources = {r['resource_id']: r for r in resources_data}

# Initialize grid and counts for Level 3
grid_size = 300
grid = np.ones((grid_size, grid_size), dtype=int)
resource_counts = {t: 0 for t in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]}
resource_sizes = {t: max(len(o['cells']) for o in resources[t]['orientations']) for t in resource_counts}
incompatible_sets = {t: set(resources[t].get('incompatible_with', [])).union({t}) for t in resource_counts}
interest_factors = {t: resources[t].get('interest_factor', 1.0) for t in resource_counts}  # Default to 1.0 if not provided

def can_place_resource(grid: np.ndarray, resource: dict, orient_idx: int, top_left: tuple[int, int], level: int = 3) -> bool:
    """Bounds, overlap, same-type spacing (L1), radius-5 incompatibility (L2+)."""
    cells = resource["orientations"][orient_idx]["cells"]
    rid = resource["resource_id"]
    occupied = []

    # 1) Bounds & overlap
    for dr, dc in cells:
        r, c = top_left[0] + dr, top_left[1] + dc
        if not in_bounds(grid, r, c) or grid[r, c] != 1:
            return False
        occupied.append((r, c))

    # 2) Level 1: no adjacent same-type
    for r, c in occupied:
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if in_bounds(grid, nr, nc) and grid[nr, nc] == rid:
                return False

    # 3) Level 2: radius-5 incompatibility
    forbidden = incompatible_sets[rid]
    R = 5
    for r, c in occupied:
        r_min, r_max = max(0, r - R), min(grid_size, r + R + 1)
        c_min, c_max = max(0, c - R), min(grid_size, c + R + 1)
        for nr in range(r_min, r_max):
            for nc in range(c_min, c_max):
                if (nr, nc) in occupied:
                    continue
                if grid[nr, nc] in forbidden:
                    return False
    return True

def place_resource(grid: np.ndarray, resource: dict, orient_idx: int, top_left: tuple[int, int]) -> None:
    """Mutate grid in place."""
    cells = resource["orientations"][orient_idx]["cells"]
    rid = resource["resource_id"]
    for dr, dc in cells:
        grid[top_left[0] + dr, top_left[1] + dc] = rid

def calculate_interest_factor(grid, resource_counts):
    """Sum interest factors within 10-block radius of each placed cell, normalized."""
    total_interest = 0.0
    placed_cells = 0
    R = 10
    for r in range(grid_size):
        for c in range(grid_size):
            if grid[r, c] == 1:
                continue
            placed_cells += 1
            r_min, r_max = max(0, r - R), min(grid_size, r + R + 1)
            c_min, c_max = max(0, c - R), min(grid_size, c + R + 1)
            for nr in range(r_min, r_max):
                for nc in range(c_min, c_max):
                    if grid[nr, nc] != 1:
                        total_interest += interest_factors[grid[nr, nc]]
    return total_interest / placed_cells if placed_cells > 0 else 1.0

def calculate_simpson_index(counts):
    total = sum(counts.values())
    if total == 0:
        return 1.0
    diversity = sum((count/total)**2 for count in counts.values() if count > 0)
    return diversity

def score_placement(grid, resource_counts):
    pathway_count = np.count_nonzero(grid == 1)
    utilized_area = grid_size * grid_size - pathway_count
    s = len([count for count in resource_counts.values() if count > 0])
    d = calculate_simpson_index(resource_counts)
    balance_multiplier = (s + 1/d) / 2 if d > 0 else s / 2
    interest_multiplier = calculate_interest_factor(grid, resource_counts)
    return utilized_area * balance_multiplier * interest_multiplier

def get_valid_placements(grid, r, c):
    placements = []
    for t in sorted_resources:
        for o_idx, o in enumerate(resources[t]['orientations']):
            if can_place_resource(grid, resources[t], o_idx, (r, c), level=3):
                placements.append((t, o_idx))
    return placements

# Sort resources by size (descending), interest factor (descending), and incompatibilities (ascending)
sorted_resources = sorted(
    resource_counts.keys(),
    key=lambda t: (resource_sizes[t], interest_factors[t], -len(incompatible_sets[t])),
    reverse=True
)

# Block-based cell order for better spatial locality
def generate_block_cells(block_size=30):
    cells = []
    for br in range(0, grid_size, block_size):
        for bc in range(0, grid_size, block_size):
            for r in range(br, min(br + block_size, grid_size)):
                for c in range(bc, min(bc + block_size, grid_size)):
                    cells.append((r, c))
    random.shuffle(cells)
    return cells

# Optimized placement
def place_resources(grid, resource_counts, max_attempts=2, block_size=30):
    best_score = 0
    best_grid = grid.copy()
    best_counts = resource_counts.copy()
    
    for attempt in range(max_attempts):
        temp_grid = np.ones((grid_size, grid_size), dtype=int)
        temp_counts = resource_counts.copy()
        cells = generate_block_cells(block_size)
        
        for r, c in cells:
            if temp_grid[r, c] != 1:
                continue
            valid_placements = get_valid_placements(temp_grid, r, c)
            if not valid_placements:
                continue
                
            # Score placements based on size, interest, and diversity
            best_placement = None
            best_score_attempt = -1
            for t, o_idx in valid_placements:
                cell_count = len(resources[t]['orientations'][o_idx]['cells'])
                temp_counts[t] += 1
                d = calculate_simpson_index(temp_counts)
                s = len([count for count in temp_counts.values() if count > 0])
                score = cell_count * (s + 1/d) / 2 * interest_factors[t]
                if score > best_score_attempt:
                    best_score_attempt = score
                    best_placement = (t, o_idx)
                temp_counts[t] -= 1
            
            if best_placement:
                t, o_idx = best_placement
                place_resource(temp_grid, resources[t], o_idx, (r, c))
                temp_counts[t] += 1
                
                # Early stopping if grid is mostly filled
                if np.count_nonzero(temp_grid == 1) < 0.15 * grid_size * grid_size:
                    break
        
        current_score = score_placement(temp_grid, temp_counts)
        if current_score > best_score:
            best_score = current_score
            best_grid = temp_grid.copy()
            best_counts = temp_counts.copy()
    
    grid[:] = best_grid
    resource_counts.update(best_counts)
    return best_score

# Run placement
final_score = place_resources(grid, resource_counts)
print(f"Estimated Score: {final_score}")
print(f"Resource counts: {resource_counts}")
print(f"Pathway cells: {np.count_nonzero(grid == 1)}")

# Output result
with open('submission.txt', 'w') as f:
    f.write('{\n  "zoo": [\n')
    for i, row in enumerate(grid):
        row_str = json.dumps(row.tolist())
        f.write(f"    {row_str},\n" if i < len(grid) - 1 else f"    {row_str}\n")
    f.write('  ]\n}')