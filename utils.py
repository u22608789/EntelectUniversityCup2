# utils.py

import json
from collections import Counter
from typing import List, Dict, Any

# — distance & bounds — 
def chebyshev_dist(x1,y1,x2,y2): return max(abs(x1-x2), abs(y1-y2))
def in_bounds(grid, r,c):      return 0 <= r < grid.shape[0] and 0 <= c < grid.shape[1]

# — Level-1 scoring — 
def simpsons_index(counts: List[int]) -> float:
    N=sum(counts)
    return 1.0 if N<2 else sum(n*(n-1) for n in counts)/(N*(N-1))

def score_level1(placements: List[Dict[str,Any]],
                 resources: Dict[int,Any]) -> Dict[str,float]:
    area = 0
    for p in placements:
        orient = next(o for o in resources[p["resource_id"]]["orientations"]
                     if o["rotation"]==p["rotation"])
        area += len(orient["cells"])
    cnt = Counter(p["resource_id"] for p in placements)
    S   = len(cnt)
    D   = simpsons_index(list(cnt.values()))
    M   = (S + 1/D)/2
    return {"area": area, "unique_types": S, "simpson_D":D, "multiplier":M, "final_score": area*M}

# — Solution output — 
def write_solution(grid: Any, path: str) -> None:
    with open(path, "w") as f:
        f.write("{\n  \"zoo\": [\n")
        for i,row in enumerate(grid):
            line = json.dumps(row)
            comma= "," if i < len(grid)-1 else ""
            f.write(f"    {line}{comma}\n")
        f.write("  ]\n}\n")
