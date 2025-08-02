import json

def load_solution_grid(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data['zoo']

def is_adjacent_same_resource(grid, r, c, val):
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                if grid[nr][nc] == val:
                    return True
    return False

def check_whole_grid_adjacency(file_path):
    grid = load_solution_grid(file_path)
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            val = grid[r][c]
            if val == 1:
                continue  # Pathway, skip
            if is_adjacent_same_resource(grid, r, c, val):
                print(f"Adjacency violation at ({r},{c}) for resource ID {val}")
                return False
    print("No adjacency violations in the solution file!")
    return True

# To run the solution checker:
print("\n--- Checking full solution.txt for adjacency constraint ---")
check_whole_grid_adjacency('solution.txt')