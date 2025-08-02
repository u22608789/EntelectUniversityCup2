# handle grid and placement

# Checking and modifying the grid
import numpy as np
from utils import chebyshev_dist, in_bounds

def can_place_resource(grid, resource, orientation, top_left, resource_by_id, forbidden_radius=5):
    """
    Checks if a resource can be placed at the given top_left (row, col) with the specified orientation.
    """
    cells = resource['orientations'][orientation]['cells']
    r_id = resource['resource_id']
    n_rows, n_cols = grid.shape
    
    occupied = []
    # Check bounds and overlap
    for dr, dc in cells:
        rr, cc = top_left[0] + dr, top_left[1] + dc
        if not in_bounds(grid, rr, cc):
            return False  
        if grid[rr, cc] != 1:
            return False  
        occupied.append((rr, cc))
        
    # Check for incompatible resources within forbidden radius 
    for rr, cc in occupied:
        for dr in range(-forbidden_radius, forbidden_radius + 1):
            for dc in range(-forbidden_radius, forbidden_radius + 1):
                nr, nc = rr + dr, cc + dc
                if not in_bounds(grid, nr, nc):
                    continue
                other_id = grid[nr, nc]
                if other_id == 1:
                    continue
                if other_id in resource['incompatible_with']:
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
