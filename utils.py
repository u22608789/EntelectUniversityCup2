# Helpers

# Distance checks 
def chebyshev_dist(x1, y1, x2, y2):
    """Calculate Chebyshev (king's move) distance between two points."""
    return max(abs(x1 - x2), abs(y1 - y2))

# Grid bounds
def in_bounds(grid, row, col):
    """Check if (row, col) is within grid bounds."""
    return 0 <= row < grid.shape[0] and 0 <= col < grid.shape[1]