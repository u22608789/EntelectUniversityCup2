import json
import random
import numpy as np
from utils import in_bounds

def load_resources(path='resources.json'):
    with open(path, 'r') as f:
        data = json.load(f)['resources']
    return {r['resource_id']: r for r in data}

# --- GLOBAL SETTINGS ---
GRID_SIZE     = 800
ATTEMPTS      = 2
BLOCK_SIZE    = 20
COST_PENALTY  = 1.0  # tune this up/down to weight cost more/less

# --- 1. Load and initialize ---
resources = load_resources()
grid = np.ones((GRID_SIZE, GRID_SIZE), dtype=int)

# Exclude pathway (ID = 1)
all_ids = [rid for rid in resources if rid != 1]

resource_counts   = {t: 0 for t in all_ids}
resource_sizes    = {t: max(len(o['cells']) for o in resources[t]['orientations']) for t in all_ids}
incompatible_sets = {t: set(resources[t].get('incompatible_with', [])) | {t} for t in all_ids}
interest_factors  = {t: resources[t].get('interest_factor', 1.0) for t in all_ids}
resource_costs    = {t: resources[t].get('cost', 1) for t in all_ids}

# Pre-sort for greedy placement (interest-per-cost)
sorted_ids = sorted(
    all_ids,
    key=lambda t: (
        interest_factors[t] / (resource_costs[t] + 1e-6),
        resource_sizes[t],
        -len(incompatible_sets[t])
    ),
    reverse=True
)

# --- 2. Optimized can_place_resource ---
def can_place_resource(temp_grid, res, o_idx, top_left):
    cells = res['orientations'][o_idx]['cells']
    rid   = res['resource_id']

    # 1) Bounds & empty
    occupied = []
    for dr, dc in cells:
        r, c = top_left[0] + dr, top_left[1] + dc
        if not in_bounds(temp_grid, r, c) or temp_grid[r, c] != 1:
            return False
        occupied.append((r, c))

    # 2) No adjacent same type
    for r, c in occupied:
        if ((r > 0            and temp_grid[r-1, c] == rid) or
            (r < GRID_SIZE-1 and temp_grid[r+1, c] == rid) or
            (c > 0            and temp_grid[r, c-1] == rid) or
            (c < GRID_SIZE-1 and temp_grid[r, c+1] == rid)):
            return False

    # 3) 5-block incompatibility (vectorized)
    forbidden = incompatible_sets[rid]
    if not forbidden:
        return True

    R = 5
    rows = [r for r,_ in occupied]
    cols = [c for _,c in occupied]
    r0 = max(min(rows) - R, 0)
    r1 = min(max(rows) + R + 1, GRID_SIZE)
    c0 = max(min(cols) - R, 0)
    c1 = min(max(cols) + R + 1, GRID_SIZE)

    sub = temp_grid[r0:r1, c0:c1]
    # mask occupied cells
    mask = np.zeros_like(sub, dtype=bool)
    for (r, c) in occupied:
        mask[r-r0, c-c0] = True

    # any forbidden ID outside mask?
    if np.any(np.isin(sub, list(forbidden)) & ~mask):
        return False

    return True

# --- 3. Place resource on grid ---
def place_resource_on_grid(temp_grid, res, o_idx, top_left):
    rid = res['resource_id']
    for dr, dc in res['orientations'][o_idx]['cells']:
        temp_grid[top_left[0]+dr, top_left[1]+dc] = rid

# --- 4. Simpson index ---
def simpson_index(counts):
    total = sum(counts.values())
    if total == 0:
        return 1.0
    return sum((v/total)**2 for v in counts.values() if v>0)

# --- 5. Approximate interest factor (Level 3) ---
def calculate_interest_factor(temp_grid, sample=20000):
    coords = np.argwhere(temp_grid != 1)
    if len(coords) == 0:
        return 1.0
    if len(coords) > sample:
        idx = np.random.choice(len(coords), sample, replace=False)
        coords = coords[idx]
    total = 0.0
    R = 10
    for r, c in coords:
        rid = temp_grid[r, c]
        base = interest_factors[rid]
        boost = 0.0
        for dr in range(-R, R+1):
            rr = r + dr
            if rr<0 or rr>=GRID_SIZE: continue
            for dc in range(-R, R+1):
                cc = c + dc
                if cc<0 or cc>=GRID_SIZE: continue
                nrid = temp_grid[rr, cc]
                if nrid != 1:
                    boost += interest_factors[nrid] * 0.10
        total += base + boost
    return total / len(coords)

# --- 6. Level 4 scoring ---
def score_grid(temp_grid, counts, total_cost):
    paths = np.count_nonzero(temp_grid==1)
    util  = GRID_SIZE*GRID_SIZE - paths
    s     = len([v for v in counts.values() if v>0])
    d     = simpson_index(counts)
    balance = (s + 1/d)/2 if d>0 else s/2
    interest = calculate_interest_factor(temp_grid)
    lvl3 = util * balance * interest
    total_cost = max(total_cost, 1)
    return lvl3 / (total_cost**COST_PENALTY)

# --- 7. Generate cell order ---
def generate_block_cells(block_size):
    cells = []
    for br in range(0, GRID_SIZE, block_size):
        for bc in range(0, GRID_SIZE, block_size):
            for r in range(br, min(br+block_size, GRID_SIZE)):
                for c in range(bc, min(bc+block_size, GRID_SIZE)):
                    cells.append((r, c))
    random.shuffle(cells)
    return cells

# --- 8. Main placement algorithm ---
def run_placement():
    best_score = 0
    best_grid  = None
    best_counts= None
    best_cost  = 0

    for _ in range(ATTEMPTS):
        temp_grid   = np.ones((GRID_SIZE, GRID_SIZE), dtype=int)
        temp_counts = {t: 0 for t in all_ids}
        total_cost  = 0

        for (r, c) in generate_block_cells(BLOCK_SIZE):
            if temp_grid[r, c] != 1:
                continue

            best_val = -1
            best_loc = None

            for t in sorted_ids:
                res = resources[t]
                for o_idx in range(len(res['orientations'])):
                    if not can_place_resource(temp_grid, res, o_idx, (r, c)):
                        continue
                    temp_counts[t] += 1
                    s = len([v for v in temp_counts.values() if v>0])
                    d = simpson_index(temp_counts)
                    val = (interest_factors[t]*len(res['orientations'][o_idx]['cells'])) / (resource_costs[t]+1e-6)
                    val *= (s + 1/d)/2
                    temp_counts[t] -= 1
                    if val > best_val:
                        best_val = val
                        best_loc = (t, o_idx)

            if best_loc:
                t, o_idx = best_loc
                place_resource_on_grid(temp_grid, resources[t], o_idx, (r, c))
                temp_counts[t] += 1
                total_cost += resource_costs[t]

        score = score_grid(temp_grid, temp_counts, total_cost)
        if score > best_score:
            best_score, best_grid, best_counts, best_cost = score, temp_grid.copy(), temp_counts.copy(), total_cost

    return best_score, best_grid, best_counts, best_cost

# --- 9. Main entrypoint ---
def main():
    final_score, final_grid, final_counts, final_cost = run_placement()

    # Update global grid & counts
    global grid, resource_counts
    grid = final_grid
    resource_counts = final_counts

    # Print summary
    print(f"Level 4 Estimated Score: {final_score:.2f}")
    print(f"Total Cost: {final_cost}")
    print(f"Resource counts: {resource_counts}")
    print(f"Pathway cells: {np.count_nonzero(grid==1)}")

    # Write submission
    with open('submission.txt', 'w') as f:
        f.write('{\n  "zoo": [\n')
        for i, row in enumerate(grid):
            line = json.dumps(row.tolist())
            f.write(line + (',\n' if i < GRID_SIZE-1 else '\n'))
        f.write('  ]\n}')

if __name__ == "__main__":
    main()
