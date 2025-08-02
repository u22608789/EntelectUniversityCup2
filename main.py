# main.py
from pathlib import Path
from resources import load_resources, parse_level
from solver import solve_level, score_level2
from utils     import score_level1, write_solution
import numpy as np

def main():
    res = load_resources(Path("resources.json"))
    lvl = parse_level   (Path("2.txt"))

    from zoo_grid import check_grid_size, check_allowed_ids
    check_grid_size(np.array(lvl["base_grid"]), lvl["level"])
    check_allowed_ids(np.array(lvl["base_grid"]), lvl["level"])
    
    out = solve_level(lvl, res)
    
    grid, placements = out["grid"], out["placements"]
    print(f"Placed {len(placements)} items.")

    stats = score_level2(placements, res, grid)
    print("Level-2 score:", stats["final_score"])
    print("Violations:", stats["violations"])
    
    write_solution(grid, "solution.txt")
    print("Wrote solution.txt")

if __name__=="__main__":
    main()
