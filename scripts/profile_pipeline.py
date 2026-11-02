"""Profile the synthetic smoke pipeline (G-R12: Theory of Constraints).

Run this before changing model architecture, solver settings, or feature code.
The script does not prove the real pipeline is fast; it shows where the current
end-to-end path spends its time, so optimization is aimed at the bottleneck.
"""

from __future__ import annotations

import argparse
import cProfile
import io
import pstats
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Profile the synthetic smoke pipeline.")
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="Number of cumulative-time functions to print (default: 20).",
    )
    args = parser.parse_args()

    profiler = cProfile.Profile()
    profiler.enable()
    runpy.run_path(str(ROOT / "scripts" / "run_smoke.py"), run_name="__main__")
    profiler.disable()

    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream).sort_stats("cumulative")
    stats.print_stats(max(1, args.top))
    print("\n=== cProfile: top cumulative functions ===")
    print(stream.getvalue())


if __name__ == "__main__":
    main()
