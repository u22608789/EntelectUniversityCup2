import json
import random
import numpy as np
from collections import Counter
from utils import in_bounds, chebyshev_dist

# --- 0. Configuration ---
QUICK_MODE = True
if QUICK_MODE:
    MAX_ATTEMPTS = 1
    SAMPLE_SIZE = 75000
    INTEREST_SAMPLES = 5000
else:
    MAX_ATTEMPTS = 2
    SAMPLE_SIZE = 100000
    INTEREST_SAMPLES = 10000

# --- 1. Load resources & metadata ---
try:
    with open('resources.json', 'r') as f:
        resources_data = json.load(f)['resources']
    resources = {r['resource_id']: r for r in resources_data}
except Exception as e:
    print(f"Error loading resources.json: {e}")
    exit(1)

# Validate resources
for r in resources.values():
    if 'resource_id' not in r or 'orientations' not in r:
        print(f"Invalid resource format: {r.get('resource_id')}")
        exit(1)

# Initialize grid and counts for Level 4
grid_size = 800
grid = np.ones((grid_size, grid_size), dtype=int)
resource_counts = {t: 0 for t in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]}
resource_sizes = {t: max(len(o['cells']) for o in resources[t]['orientations']) for t in resource_counts}
incompatible_sets = {t: set(resources[t].get('incompatible_with', [])).union({t}) for t in resource_counts}
interest_factors = {t: resources[t].get('interest_factor', 1.0) for t in resource_counts}
costs = {t: resources[t].get('cost', 1.0) for t in resource_counts}

# --- 2. Precompute neighbor offsets ---
radius5 = [(dr, dc) for dr in range(-5, 6) for dc in range(-5, 6)]
radius10 = [(dr, dc) for dr in range(-10, 11) for dc in range(-10, 11)]

# --- 3. Placement check & action ---
def can_place_resource(grid, resource, orient_idx, top_left, level=4):
    cells = resource["orientations"][orient_idx]["cells"]
    rid = resource["resource_id"]
    occupied = []
    for dr, dc in cells:
        r, c = top_left[0] + dr, top_left[1] + dc
        if not in_bounds(grid, r, c) or grid[r, c] != 1:
            return False
        occupied.append((r, c))
    for r, c in occupied:
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if in_bounds(grid, nr, nc) and grid[nr, nc] == rid:
                return False
    forbidden = incompatible_sets[rid]
    R = 5
    for r, c in occupied:
        for dr, dc in radius5:
            nr, nc = r + dr, c + dc
            if (nr, nc) in set(occupied):
                continue
            if 0 <= nr < grid_size and 0 <= nc < grid_size and grid[nr, nc] in forbidden:
                return False
    return True

def place_resource(grid, resource, orient_idx, top_left, record=None):
    cells = resource["orientations"][orient_idx]["cells"]
    rid = resource["resource_id"]
    for dr, dc in cells:
        grid[top_left[0] + dr, top_left[1] + dc] = rid
    if record is not None:
        record.append({"resource": resource, "orient_idx": orient_idx, "top_left": top_left})

# --- 4. Interest and scoring ---
def calculate_proximity_boost(grid, r, c, cells):
    boost = 0.0
    sample_size = 50
    for dr, dc in cells:
        nr, nc = r + dr, c + dc
        cells_to_check = [(nr + dr2, nc + dc2) for dr2, dc2 in radius10 if 0 <= nr + dr2 < grid_size and 0 <= nc + dc2 < grid_size]
        if len(cells_to_check) > sample_size:
            cells_to_check = random.sample(cells_to_check, sample_size)
        boost += sum(0.10 * interest_factors[grid[nr, nc]] for nr, nc in cells_to_check if grid[nr, nc] != 1)
    return boost / len(cells) if cells else 0.0

def compute_level4_score(grid, placements, counts):
    interest_grid = np.zeros((grid_size, grid_size), dtype=float)
    total_cost = 0.0
    for p in placements:
        total_cost += p["resource"].get("cost", 1.0)
        for r, c in [(p["top_left"][0] + dr, p["top_left"][1] + dc) for dr, dc in p["resource"]["orientations"][p["orient_idx"]]["cells"]]:
            interest_grid[r, c] = p["resource"]["interest_factor"]
    
    interest_score = 0.0
    sampled = random.sample(placements, min(INTEREST_SAMPLES, len(placements))) if len(placements) > INTEREST_SAMPLES else placements
    for p in sampled:
        base_if = p["resource"]["interest_factor"]
        boost = 0.0
        cells = [(p["top_left"][0] + dr, p["top_left"][1] + dc) for dr, dc in p["resource"]["orientations"][p["orient_idx"]]["cells"]]
        sample_cells = random.sample(cells, min(10, len(cells))) if len(cells) > 10 else cells
        for r, c in sample_cells:
            cells_to_check = [(r + dr, c + dc) for dr, dc in radius10 if 0 <= r + dr < grid_size and 0 <= c + dc < grid_size]
            if len(cells_to_check) > 50:
                cells_to_check = random.sample(cells_to_check, 50)
            boost += sum(0.10 * interest_grid[nr, nc] for nr, nc in cells_to_check if interest_grid[nr, nc] > 0)
        interest_score += (base_if + boost / len(sample_cells)) * (len(placements) / max(1, len(sampled)))
    
    utilized_area = grid_size * grid_size - np.count_nonzero(grid == 1)
    s = len([count for count in counts.values() if count > 0])
    d = sum((count/sum(counts.values()))**2 for count in counts.values() if count > 0) if sum(counts.values()) > 0 else 1.0
    balance_multiplier = (s + 1/d) / 2 if d > 0 else s / 2
    gross_score = (interest_score * utilized_area * balance_multiplier) / 10000
    return gross_score / (1 + total_cost / 10_000_000), total_cost

# --- 5. Placement logic ---
def get_valid_placements(grid, r, c, cache):
    cache_key = (r, c, hash(tuple(grid[max(0, r-5):r+6, max(0, c-5):c+6].ravel())))
    if cache_key in cache:
        return cache[cache_key]
    
    placements = []
    for t in sorted_resources:
        for o_idx in range(len(resources[t]['orientations'])):
            if can_place_resource(grid, resources[t], o_idx, (r, c), level=4):
                placements.append((t, o_idx))
    cache[cache_key] = placements
    return placements

# Sort resources by interest-to-cost ratio, size, and incompatibilities
sorted_resources = sorted(
    resource_counts.keys(),
    key=lambda t: (interest_factors[t] / max(costs[t], 1e-6), resource_sizes[t], -len(incompatible_sets[t])),
    reverse=True
)

# Spiral cell order
def generate_sampled_cells(sample_size=SAMPLE_SIZE):
    cells = []
    x, y = grid_size // 2, grid_size // 2
    dx, dy = 0, -1
    steps, step_count = 1, 0
    direction_changes = 0
    while len(cells) < sample_size:
        if 0 <= x < grid_size and 0 <= y < grid_size:
            cells.append((x, y))
        x, y = x + dx, y + dy
        step_count += 1
        if step_count == steps:
            step_count = 0
            dx, dy = -dy, dx
            direction_changes += 1
            if direction_changes == 2:
                steps += 1
                direction_changes = 0
    random.shuffle(cells)
    return cells

# Optimized placement
def place_resources(grid, resource_counts, max_attempts=MAX_ATTEMPTS):
    best_score = 0
    best_grid = grid.copy()
    best_counts = resource_counts.copy()
    best_placements = []
    cache = {}
    
    for attempt in range(max_attempts):
        temp_grid = np.ones((grid_size, grid_size), dtype=int)
        temp_counts = resource_counts.copy()
        placements = []
        cells = generate_sampled_cells()
        total_cost = 0.0
        
        for r, c in cells:
            if temp_grid[r, c] != 1:
                continue
            valid_placements = get_valid_placements(temp_grid, r, c, cache)
            if not valid_placements:
                continue
                
            best_placement = None
            best_score_attempt = -1
            total_resources = max(1, sum(temp_counts.values()))
            for t, o_idx in valid_placements:
                cell_count = len(resources[t]['orientations'][o_idx]['cells'])
                temp_counts[t] += 1
                s = len([count for count in temp_counts.values() if count > 0])
                d = sum((count/total_resources)**2 for count in temp_counts.values() if count > 0) if total_resources > 0 else 1.0
                balance_score = (s + 1/d) / 2 if d > 0 else s / 2
                boost = calculate_proximity_boost(temp_grid, r, c, resources[t]['orientations'][o_idx]['cells'])
                individual_score = interest_factors[t] + boost
                cost = resources[t].get('cost', 1.0)
                overuse_penalty = 1.0 / (1 + 3 * temp_counts[t] / total_resources)
                cost_penalty = 20_000_000 / (10_000_000 + cost)
                score = cell_count * individual_score * balance_score * overuse_penalty * cost_penalty
                if score > best_score_attempt:
                    best_score_attempt = score
                    best_placement = (t, o_idx)
                temp_counts[t] -= 1
            
            if best_placement:
                t, o_idx = best_placement
                place_resource(temp_grid, resources[t], o_idx, (r, c), placements)
                temp_counts[t] += 1
                total_cost += resources[t].get('cost', 1.0)
                
                if np.count_nonzero(temp_grid == 1) < 0.15 * grid_size * grid_size:
                    break
        
        current_score, current_cost = compute_level4_score(temp_grid, placements, temp_counts)
        if current_score > best_score:
            best_score = current_score
            best_grid = temp_grid.copy()
            best_counts = temp_counts.copy()
            best_placements = placements.copy()
    
    grid[:] = best_grid
    resource_counts.update(best_counts)
    return best_score, best_placements, total_cost

# --- 6. Run & export ---
try:
    final_score, placements, total_cost = place_resources(grid, resource_counts)
    print(f"Estimated Level 4 Score: {final_score:.2f}")
    print(f"Total Cost: {total_cost}")
    print(f"Resource counts: {resource_counts}")
    print(f"Pathway cells: {np.count_nonzero(grid == 1)}")
except Exception as e:
    print(f"Error during placement: {e}")
    exit(1)

try:
    with open('submission.txt', 'w') as f:
        f.write('{\n  "zoo": [\n')
        for i, row in enumerate(grid):
            row_str = json.dumps(row.tolist())
            f.write(f"    {row_str},\n" if i < len(grid) - 1 else f"    {row_str}\n")
        f.write('  ]\n}')
except Exception as e:
    print(f"Error writing submission.txt: {e}")
    exit(1)