import json
import re
from pathlib import Path
from typing import List, Dict, Any, NamedTuple

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
    resources = {}
    for r in data["resources"]:
        res = Resource(
            resource_id=r["resource_id"],
            name=r["name"],
            type=r["type"],
            bounding_box=r["bounding_box"],
            cost=r["cost"],
            interest_factor=r["interest_factor"],
            incompatible_with=r["incompatible_with"],
            orientations=r["orientations"]
        )
        resources[res.resource_id] = res
    return resources

def _extract_bracket_block(s: str, start_pat: str) -> str:
    """Find the first '[' after start_pat in s, then return the substring
    from that '[' through its matching closing ']' (accounting for nesting)."""
    start_idx = s.find(start_pat)
    if start_idx < 0:
        raise ValueError(f"Couldn’t find “{start_pat}” in text")
    # find the very first '[' after that
    i = s.find('[', start_idx)
    if i < 0:
        raise ValueError("No '[' found after marker")
    depth = 0
    for j, ch in enumerate(s[i:], start=i):
        if ch == '[':
            depth += 1
        elif ch == ']':
            depth -= 1
            if depth == 0:
                return s[i:j+1]
    raise ValueError("Unmatched '[' in text")

def parse_level(path: Path) -> Dict[str, Any]:
    text = path.read_text()
    # Level number
    level_num = int(re.search(r"Level Number:\s*(\d+)", text).group(1))
    # Zoo Size
    rows, cols = map(int, re.search(r"Zoo Size:\s*(\d+)x(\d+)", text).groups())
    # Available Resources (use literal_eval or json.loads on the bracket block)
    avail_block = _extract_bracket_block(text, "Available Resources:")
    available = json.loads(avail_block)
    # Base Zoo grid
    grid_block = _extract_bracket_block(text, "Base Zoo:")
    base_grid = json.loads(grid_block)

    return {
        "level": level_num,
        "rows": rows,
        "cols": cols,
        "available_resources": available,
        "base_grid": base_grid
    }

if __name__ == "__main__":
    res_dict = load_resources(Path("resources.json"))
    level1 = parse_level(Path("1.txt"))
    print(f"Loaded Level {level1['level']} ({level1['rows']} x {level1['cols']})")
    print(f"{len(res_dict)} resource types available in JSON")
    print(f"Level 1 allows resources: {level1['available_resources']}")
    print(f"Base grid is a {len(level1['base_grid'])} x {len(level1['base_grid'][0])} array")
