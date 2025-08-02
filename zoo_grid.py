# zoo_grid.py

import numpy as np
from utils import in_bounds

ALLOWED_IDS_LEVEL_1 = set([1, 3, 4, 6, 9, 10, 11, 14, 15, 20, 21])

class ZooGrid:
    def __init__(self, base_grid, resources, level=1):
        """
        base_grid: 2D list or np.array, initial grid (should be filled with 1s for pathways)
        resources: dict of resource_id -> resource definition (Resource NamedTuple or dict)
        level: int, currently we focus on level 1
        """
        self.grid = np.array(base_grid, dtype=int)
        self.resources = resources
        self.level = level
        self.placements = []  # Each: {'resource_id', 'top_left', 'rotation'}
        self._check_grid_size()
        self._check_allowed_ids()

    def _check_grid_size(self):
        if self.level == 1 and self.grid.shape != (50, 50):
            raise ValueError(f"Level 1 grid must be 50x50, but got {self.grid.shape}")

    def _check_allowed_ids(self):
        allowed_ids = ALLOWED_IDS_LEVEL_1
        for r in range(self.grid.shape[0]):
            for c in range(self.grid.shape[1]):
                val = self.grid[r, c]
                if val not in allowed_ids:
                    raise ValueError(f"Invalid resource ID {val} at ({r},{c}) for Level {self.level}")

    def can_place(self, resource, orientation, top_left):
        """
        Checks if a resource can be placed at the given top_left (row, col) with the specified orientation (Level 1 only).
        """
        cells = resource['orientations'][orientation]['cells']
        r_id = resource['resource_id']

        occupied = []
        for dr, dc in cells:
            rr, cc = top_left[0] + dr, top_left[1] + dc
            if not in_bounds(self.grid, rr, cc):
                return False
            if self.grid[rr, cc] != 1:  # Only place on pathways
                return False
            occupied.append((rr, cc))

        # Level 1: ensure no adjacent same resource (except itself)
        for rr, cc in occupied:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = rr + dr, cc + dc
                    if in_bounds(self.grid, nr, nc) and self.grid[nr, nc] == r_id:
                        return False
        return True

    def place(self, resource, orientation, top_left):
        """
        Place resource on the grid (mutates the grid and logs placement).
        """
        cells = resource['orientations'][orientation]['cells']
        r_id = resource['resource_id']
        for dr, dc in cells:
            rr, cc = top_left[0] + dr, top_left[1] + dc
            self.grid[rr, cc] = r_id
        # Record placement
        placement = self.make_placement(r_id, top_left, orientation)
        self.placements.append(placement)

    def remove(self, resource, orientation, top_left):
        """
        Remove resource from the grid (sets those cells back to pathway).
        """
        cells = resource['orientations'][orientation]['cells']
        for dr, dc in cells:
            rr, cc = top_left[0] + dr, top_left[1] + dc
            self.grid[rr, cc] = 1
        # Remove from placements (if exists)
        to_remove = None
        for p in self.placements:
            if (p['resource_id'] == resource['resource_id'] and
                p['top_left'] == top_left and
                p['rotation'] == orientation):
                to_remove = p
                break
        if to_remove:
            self.placements.remove(to_remove)

    @staticmethod
    def make_placement(resource_id, top_left, orientation):
        """
        Helper to create a placement record.
        """
        return {
            "resource_id": resource_id,
            "top_left": top_left,
            "rotation": orientation
        }

    def print(self):
        """
        Simple ASCII grid print for debugging.
        """
        for row in self.grid:
            print(' '.join(f'{x:2}' for x in row))

    def get_placement_at(self, row, col):
        """
        Returns the placement dict if (row, col) is part of any placed resource, else None.
        """
        for placement in self.placements:
            resource_id, (base_r, base_c), orientation = (
                placement["resource_id"], placement["top_left"], placement["rotation"]
            )
            resource = self.resources[resource_id]
            cells = resource['orientations'][orientation]['cells']
            if any(base_r + dr == row and base_c + dc == col for dr, dc in cells):
                return placement
        return None
