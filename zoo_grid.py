# handle grid and placement

# zoo_grid.py

from typing import Dict, List, Any

class ZooGrid:
    def __init__(self,
                 base_grid: List[List[int]],
                 resources: Dict[int, Any]):
        self.rows = len(base_grid)
        self.cols = len(base_grid[0])
        # True if non-pathway (cell != 1) or already filled
        self.occupancy    = [[cell != 1 for cell in row] for row in base_grid]
        # Full resource_id grid (so dumping solution is trivial)
        self.resource_grid= [row.copy() for row in base_grid]
        self.resources    = resources
        self.placements   = []  # List of dicts with placement info

    def can_place(self,
                  rid: int,
                  orient: Dict[str, Any],
                  top: int,
                  left: int) -> bool:
        """Level-1: just bounds & overlap."""
        for dr, dc in orient["cells"]:
            r, c = top+dr, left+dc
            if not (0 <= r < self.rows and 0 <= c < self.cols):
                return False
            if self.occupancy[r][c]:
                return False
        return True

    def place(self,
              rid: int,
              orient: Dict[str, Any],
              top: int,
              left: int) -> None:
        """Mark occupancy & record placement."""
        for dr, dc in orient["cells"]:
            r, c = top+dr, left+dc
            self.occupancy[r][c]     = True
            self.resource_grid[r][c] = rid
        self.placements.append({
            "resource_id": rid,
            "rotation":    orient["rotation"],
            "top":         top,
            "left":        left
        })

    def fill_greedy(self, avail_ids: List[int]) -> None:
        """Greedy Level-1 fill: try largest shapes first."""
        items = []
        for rid in avail_ids:
            res = self.resources[rid]
            for orient in res.orientations:
                items.append((rid, orient, len(orient["cells"])))
        items.sort(key=lambda x: x[2], reverse=True)

        placed = True
        while placed:
            placed = False
            for rid, orient, _ in items:
                for i in range(self.rows):
                    if placed: break
                    for j in range(self.cols):
                        if self.can_place(rid, orient, i, j):
                            self.place(rid, orient, i, j)
                            placed = True
                            break
                    if placed:
                        break
