import math
from collections import Counter
from typing import List, Dict, Any

def simpsons_index(counts: List[int]) -> float:
    """
    Simpson's Diversity Index D = sum(n_i * (n_i-1)) / (N*(N-1))
    Returns D in (0,1], so 1/D≥1.
    """
    N = sum(counts)
    if N < 2:
        return 1.0
    num = sum(n*(n-1) for n in counts)
    den = N*(N-1)
    return num/den if den>0 else 1.0

def score_level1(placements: List[Dict[str, Any]],
                 resources: Dict[int, Any]) -> Dict[str, float]:
    # 1) Area = sum of cells per placement
    area = sum(len(resources[p["resource_id"]]
                    .orientations[0]["cells"])
               for p in placements)
    # 2) Diversity: count placements by resource_id
    cnt = Counter(p["resource_id"] for p in placements)
    S = len(cnt)                              # unique types
    D = simpsons_index(list(cnt.values()))    # Simpson's D
    multiplier = (S + 1/D) / 2
    score = area * multiplier

    return {
        "area": area,
        "unique_types": S,
        "simpson_D": D,
        "multiplier": multiplier,
        "final_score": score
    }
