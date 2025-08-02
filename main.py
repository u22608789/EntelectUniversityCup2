import json

# Load resources
with open('resources.json', 'r') as f:
    resources_data = json.load(f)['resources']
resources = {r['resource_id']: r for r in resources_data}

# Initialize grid and counts
grid = [[1 for _ in range(50)] for _ in range(50)]
resource_counts = {t: 0 for t in [3, 4, 6, 9, 10, 11, 14, 15, 20, 21]}

def can_place(grid, r, c, res_id, orientation, size=50):
    cells = orientation['cells']
    # Check bounds and overlap
    for dr, dc in cells:
        nr, nc = r + dr, c + dc
        if not (0 <= nr < size and 0 <= nc < size and grid[nr][nc] == 1):
            return False
    # Check adjacency for same resource
    for dr, dc in cells:
        nr, nc = r + dr, c + dc
        for ar, ac in [(nr-1, nc), (nr+1, nc), (nr, nc-1), (nr, nc+1)]:
            if (0 <= ar < size and 0 <= ac < size and grid[ar][ac] == res_id):
                return False
    return True

def place_resource(grid, r, c, res_id, orientation):
    for dr, dc in orientation['cells']:
        grid[r + dr][c + dc] = res_id

# Greedy placement
for r in range(50):
    for c in range(50):
        if grid[r][c] != 1:
            continue
        valid_placements = []
        for t in resource_counts.keys():
            for o in resources[t]['orientations']:
                if can_place(grid, r, c, t, o):
                    valid_placements.append((t, o))
        if valid_placements:
            # Choose resource with min count
            min_count = min(resource_counts[t] for t, _ in valid_placements)
            candidates = [(t, o) for t, o in valid_placements if resource_counts[t] == min_count]
            t, o = min(candidates, key=lambda x: x[0])  # Smallest ID if tied
            place_resource(grid, r, c, t, o)
            resource_counts[t] += 1

# Output result with each row on a new line
with open('submission.txt', 'w') as f:
    f.write('{\n  "zoo": [\n')
    for i, row in enumerate(grid):
        row_str = json.dumps(row)
        if i < len(grid) - 1:
            f.write(f"    {row_str},\n")
        else:
            f.write(f"    {row_str}\n")
    f.write('  ]\n}')
