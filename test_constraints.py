import numpy as np
from zoo_grid import can_place_resource, place_resource, print_grid

# 7x7 grid, all pathways
grid = np.ones((7, 7), dtype=int)

resources = [
    {
        'resource_id': 2,
        'orientations': {
            0: {'cells': [(0,0), (0,1)]},  # horizontal 2-block
            1: {'cells': [(0,0), (1,0)]}   # vertical 2-block
        },
        'incompatible_with': [3],
    },
    {
        'resource_id': 3,
        'orientations': {
            0: {'cells': [(0,0), (1,0)]},   # vertical 2-block
        },
        'incompatible_with': [2],
    }
]

print("A. Place resource 2 at (2,2) horizontal (level 1):")
print(can_place_resource(grid, resources[0], 0, (2,2), level=1))  # True
place_resource(grid, resources[0], 0, (2,2))
print_grid(grid)

print("B. Try to place resource 2 at (2,3) horizontal (adjacent, level 1):")
print(can_place_resource(grid, resources[0], 0, (2,3), level=1))  # False
print_grid(grid)

print("C. Place resource 3 at (0,0), vertical (level 1):")
print(can_place_resource(grid, resources[1], 0, (0,0), level=1))  # True
place_resource(grid, resources[1], 0, (0,0))
print_grid(grid)

print("D. Try to place resource 3 at (4,2), vertical (level 2):")
print(can_place_resource(grid, resources[1], 0, (4,2), level=2))  # False

print("E. Try to place resource 3 at (6,0), vertical (level 2):")
print(can_place_resource(grid, resources[1], 0, (6,0), level=2))  # True

# --- Additional checks ---

print("F. Try to place resource 2 OVERLAPPING at (2,2), vertical (level 1):")
print(can_place_resource(grid, resources[0], 1, (2,2), level=1))  # False (overlaps with 2)

print("G. Try to place resource 2 at grid edge (6,5), horizontal (level 1):")
print(can_place_resource(grid, resources[0], 0, (6,5), level=1))  # True (should fit at edge)
place_resource(grid, resources[0], 0, (6,5))
print_grid(grid)

print("H. Try to place resource 2 OUT OF BOUNDS at (6,6), horizontal (level 1):")
print(can_place_resource(grid, resources[0], 0, (6,6), level=1))  # False (out of bounds)

print("I. Try to place resource 3 NOT ADJACENT at (4,5), vertical (level 1):")
print(can_place_resource(grid, resources[1], 0, (4,5), level=1))  # True
place_resource(grid, resources[1], 0, (4,5))
print_grid(grid)

print("J. Try to place resource 3 at (5,5), vertical (level 1) -- overlaps with previous:")
print(can_place_resource(grid, resources[1], 0, (5,5), level=1))  # False (overlap)

print("K. Try to place resource 2 at (0,5), vertical (level 1) -- test orientation 1:")
print(can_place_resource(grid, resources[0], 1, (0,5), level=1))  # True
place_resource(grid, resources[0], 1, (0,5))
print_grid(grid)

print("L. Try to place resource 2 at (1,5), vertical (level 2) -- forbidden by incompatible_with=3 radius-5?")
print(can_place_resource(grid, resources[0], 1, (1,5), level=2))  # Should be False due to forbidden radius w.r.t. resource 3 at (4,5)
