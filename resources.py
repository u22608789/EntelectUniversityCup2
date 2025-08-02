# resources.py

import json, re
from pathlib import Path
from typing import Any, Dict, List

def load_resources(path: Path) -> Dict[int, Dict[str, Any]]:
    """Load master resource definitions from JSON, returning a dict of plain dicts."""
    data = json.loads(path.read_text())
    return { r["resource_id"]: r for r in data["resources"] }

def _extract_bracket_block(s: str, marker: str) -> str:
    idx = s.find(marker)
    if idx < 0:
        raise ValueError(f"Couldn’t find “{marker}”")
    i = s.find("[", idx)
    depth = 0
    for j,ch in enumerate(s[i:], start=i):
        if   ch == "[": depth += 1
        elif ch == "]": depth -= 1
        if depth == 0:
            return s[i:j+1]
    raise ValueError("Unmatched brackets")

def parse_level(path: Path) -> Dict[str, Any]:
    """Parse level-file (1.txt, 2.txt, ...) into a dict with level, grid, etc."""
    text = path.read_text()
    level_num = int(re.search(r"Level Number:\s*(\d+)", text).group(1))
    rows, cols = map(int, re.search(r"Zoo Size:\s*(\d+)x(\d+)", text).groups())
    avail_block = _extract_bracket_block(text, "Available Resources:")
    base_block  = _extract_bracket_block(text, "Base Zoo:")
    return {
        "level": level_num,
        "rows": rows,
        "cols": cols,
        "available_resources": json.loads(avail_block),
        "base_grid": json.loads(base_block)
    }
