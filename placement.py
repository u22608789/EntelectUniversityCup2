# placement.py

from typing import Dict, List, Any


class PlacementEngine:
    def __init__(self,
                 base_grid: List[List[int]],
                 resources: Dict[int, Any]):
        """
        base_grid: 2D list of ints (resource_id in each cell)
        resources: dict of Resource objects keyed by resource_id
        """
        self.rows = len(base_grid)
        self.cols = len(base_grid[0])
        # Occupied if base_grid cell != 1 (pathway) or we've placed somethin    g
        self.occupancy = [
            [cell != 1 for cell in row]
            for row in base_grid
        ]
        self.resources = resources

        # Keep a full grid of resource_ids, so we can dump it at the end
        # (1 means pathway; other IDs will replace these as we place)
        self.resource_grid = [row.copy() for row in base_grid]

        # track placements as (resource_id, rotation, top_row, left_col)
        self.placements: List[Dict[str, Any]] = []

    def can_place(self,
                  resource_id: int,
                  orientation: Dict[str, Any],
                  top: int,
                  left: int) -> bool:
        """
        Check bounds & overlap for this orientation at (top,left).
        (Level 1 only needs these two checks.)
        """
        for dr, dc in orientation["cells"]:
            r = top + dr
            c = left + dc
            # 1) Must lie inside grid
            if not (0 <= r < self.rows and 0 <= c < self.cols):
                return False
            # 2) Must not already be occupied
            if self.occupancy[r][c]:
                return False
        return True

    def place(self,
              resource_id: int,
              orientation: Dict[str, Any],
              top: int,
              left: int) -> None:
        """
        Marks occupancy and records placement.
        """
        # mark cells as occupied
        for dr, dc in orientation["cells"]:
            r, c = top+dr, left+dc
            self.occupancy[r][c]    = True
            self.resource_grid[r][c] = resource_id

        # record it
        self.placements.append({
            "resource_id": resource_id,
            "rotation": orientation["rotation"],
            "top": top,
            "left": left
        })

    def fill_greedy(self, avail_ids: List[int]):
        """
        Repeatedly try to place any resource in descending size order
        until no more placements are possible.
        """
        # 1) Build a list of (rid, orient) for every orientation of each avail resource
        items = []
        for rid in avail_ids:
            res = self.resources[rid]
            for orient in res.orientations:
                cells = orient["cells"]
                items.append((rid, orient, len(cells)))
        # 2) Sort by descending cell-count
        items.sort(key=lambda x: x[2], reverse=True)

        placed_any = True
        while placed_any:
            placed_any = False
            for rid, orient, _ in items:
                # scan for the first spot that fits
                for i in range(self.rows):
                    if placed_any:
                        break
                    for j in range(self.cols):
                        if self.can_place(rid, orient, i, j):
                            self.place(rid, orient, i, j)
                            placed_any = True
                            break
                    if placed_any:
                        break
            # loop again if we placed at least one

        return  # all done
