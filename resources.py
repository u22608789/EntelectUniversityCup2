# Handle resource definitions and parsing

# resources.py

import json
import re
from pathlib import Path
from typing import NamedTuple, List, Dict, Any

class Resource(NamedTuple):
    resource_id: int
    name: str
    type: str
    bounding_box: int
    cost: int
    interest_factor: float
    incompatible_with: List[int]
    orientations: List[Dict[str, Any]]

def load_resources(path: Path) -> Dict[int, Resource]:
    data = json.loads(path.read_text())
    resources: Dict[int, Resource] = {}
    for r in data["resources"]:
        res = Resource(
            resource_id      = r["resource_id"],
            name             = r["name"],
            type             = r["type"],
            bounding_box     = r["bounding_box"],
            cost             = r["cost"],
            interest_factor  = r["interest_factor"],
            incompatible_with= r["incompatible_with"],
            orientations     = r["orientations"]
        )
        resources[res.resource_id] = res
    return resources

def _extract_bracket_block(s: str, start_pat: str) -> str:
    idx = s.find(start_pat)
    if idx < 0:
        raise ValueError(f"Couldn’t find “{start_pat}”")
    i = s.find('[', idx)
    depth = 0
    for j, ch in enumerate(s[i:], start=i):
        if   ch == '[': depth += 1
        elif ch == ']': depth -= 1
        if depth == 0:
            return s[i:j+1]
    raise ValueError("Unmatched brackets in text")

def parse_level(path: Path) -> Dict[str, Any]:
    text = path.read_text()
    # Level number
    level_num = int(re.search(r"Level Number:\s*(\d+)", text).group(1))
    # Grid size
    rows, cols = map(int, re.search(r"Zoo Size:\s*(\d+)x(\d+)", text).groups())
    # Available Resources array
    avail_block = _extract_bracket_block(text, "Available Resources:")
    available   = json.loads(avail_block)
    # Base grid
    grid_block  = _extract_bracket_block(text, "Base Zoo:")
    base_grid   = json.loads(grid_block)

    return {
        "level": level_num,
        "rows": rows,
        "cols": cols,
        "available_resources": available,
        "base_grid": base_grid
    }
