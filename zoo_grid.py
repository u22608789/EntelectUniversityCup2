# handle grid and placement

# Checking and modifying the grid
import numpy as np
from utils import chebyshev_dist, in_bounds

def can_place_resource(grid, resource, orientation, top_left, level=1):
    """
    Checks if a resource can be placed at the given top_left (row, col) with the specified orientation.
    Handles Level 1 and Level 2+ (radius-5 incompatibility).
    """
    cells = resource['orientations'][orientation]['cells']
    r_id = resource['resource_id']

    occupied = []
    # Check bounds and overlap
    for dr, dc in cells:
        rr, cc = top_left[0] + dr, top_left[1] + dc
        if not in_bounds(grid, rr, cc):
            return False
        if grid[rr, cc] != 1:  # Only place on pathways
            return False
        occupied.append((rr, cc))

    # If Level 1, check for adjacent occupied cells
    if level == 1:
        for rr, cc in occupied:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = rr + dr, cc + dc
                    if in_bounds(grid, nr, nc) and grid[nr, nc] == r_id:
                        return False
        return True

    # If Level 2+, check for incompatible resources within a radius of 5
    forbidden_radius = 5
    incompatible = set(resource.get('incompatible_with', []))
    for rr, cc in occupied:
        for dr in range(-forbidden_radius, forbidden_radius + 1):
            for dc in range(-forbidden_radius, forbidden_radius + 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = rr + dr, cc + dc
                if not in_bounds(grid, nr, nc):
                    continue
                other_id = grid[nr, nc]
                if other_id == 1:
                    continue
                # Check for incompatible IDs (including itself)
                if other_id in incompatible:
                    # Allow overlap on the current resource's own cells
                    if other_id == r_id and (nr, nc) in occupied:
                        continue
                    return False
    return True

def place_resource(grid, resource, orientation, top_left):
    """
    Place resource on the grid (mutates the grid!).
    """
    cells = resource['orientations'][orientation]['cells']
    r_id = resource['resource_id']
    for dr, dc in cells:
        rr, cc = top_left[0] + dr, top_left[1] + dc
        grid[rr, cc] = r_id

def print_grid(grid):
    """
    Simple ASCII grid print for debugging.
    """
    for row in grid:
        print(' '.join(f'{x:2}' for x in row))