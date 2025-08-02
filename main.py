from pathlib import Path
from parser import load_resources, parse_level
from placement import PlacementEngine
from scorer import score_level1
import json

# parse
resources = load_resources(Path("resources.json"))
level = parse_level(Path("1.txt"))

# fill
engine = PlacementEngine(level["base_grid"], resources)
engine.fill_greedy(level["available_resources"])
print(f"Placed {len(engine.placements)} items total.")

# score
results = score_level1(engine.placements, resources)
print("Level-1 results:")
print(f"  Area: {results['area']}")
print(f"  Unique types: {results['unique_types']}")
print(f"  Simpson's D: {results['simpson_D']:.4f}")
print(f"  Multiplier: {results['multiplier']:.4f}")
print(f"  Final score: {results['final_score']:.2f}")



output = { "zoo": engine.resource_grid }
with open("solution.txt", "w") as f:
    f.write("{\n  \"zoo\": [\n")
    grid = engine.resource_grid
    for i, row in enumerate(grid):
        row_json = json.dumps(row)                # renders “[6, 6, 6, …]”
        comma   = "," if i < len(grid)-1 else ""  # comma after every row but the last
        f.write(f"    {row_json}{comma}\n")
    f.write("  ]\n}\n")