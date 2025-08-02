# Helpers

# utils.py

import json
from collections import Counter
from typing import List, Dict, Any

def simpsons_index(counts: List[int]) -> float:
    N = sum(counts)
    if N < 2:
        return 1.0
    num = sum(n*(n-1) for n in counts)
    den = N*(N-1)
    return num/den if den>0 else 1.0

def score_level1(placements: List[Dict[str, Any]],
                 resources: Dict[int, Any]) -> Dict[str, float]:
    # total area = sum of orientation cell‐counts
    area = 0
    for p in placements:
        orients = resources[p["resource_id"]].orientations
        cells   = next(o["cells"] for o in orients if o["rotation"]==p["rotation"])
        area   += len(cells)

    cnt = Counter(p["resource_id"] for p in placements)
    S    = len(cnt)
    D    = simpsons_index(list(cnt.values()))
    mult = (S + 1/D) / 2
    return {
        "area":         area,
        "unique_types": S,
        "simpson_D":    D,
        "multiplier":   mult,
        "final_score":  area * mult
    }

def write_solution(grid: List[List[int]], path: str) -> None:
    with open(path, "w") as f:
        f.write("{\n  \"zoo\": [\n")
        for i, row in enumerate(grid):
            row_json = json.dumps(row)
            comma    = "," if i < len(grid)-1 else ""
            f.write(f"    {row_json}{comma}\n")
        f.write("  ]\n}\n")
