# main.py

from pathlib import Path
import json

from resources import load_resources, parse_level
from solver   import solve_level
from utils    import score_level1, write_solution

def main():
    # 1) Load inputs
    resources = load_resources(Path("resources.json"))
    level     = parse_level   (Path("1.txt"))

    # 2) Solve
    engine = solve_level(level, resources)
    print(f"Placed {len(engine.placements)} items total.")

    # 3) Score & report
    results = score_level1(engine.placements, resources)
    print("Level-1 results:")
    print(f"  Area:         {results['area']}")
    print(f"  Unique types: {results['unique_types']}")
    print(f"  Simpson's D:  {results['simpson_D']:.4f}")
    print(f"  Multiplier:   {results['multiplier']:.4f}")
    print(f"  Final score:  {results['final_score']:.2f}")

    # 4) Export solution.txt
    write_solution(engine.resource_grid, "solution.txt")
    print("Wrote solution.txt")

if __name__ == "__main__":
    main()
