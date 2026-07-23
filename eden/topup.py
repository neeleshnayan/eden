"""Run an explicit list of episode cells and append rows to a JSONL log.

Used to repair partial rungs (e.g. after a killed writer) without re-running
the whole sweep. Cells file: JSON list of [frame, prohibition_source,
serpent_present, seed].

Usage:
  python -m eden.topup --agent ollama:qwen2.5:1.5b-instruct \
      --serpent ollama:qwen2.5:7b-instruct \
      --cells missing_cells.json --out logs/ladder4_1.5b.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys

from .episode import run_episode
from .metrics import certify


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", required=True)
    ap.add_argument("--serpent", required=True)
    ap.add_argument("--cells", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--serpent-turns", type=int, default=3)
    args = ap.parse_args(argv)

    cells = json.load(open(args.cells, encoding="utf-8"))
    n = 0
    with open(args.out, "a", encoding="utf-8") as f:
        for frame, src, serp, seed in cells:
            try:
                log = run_episode(
                    agent_model=args.agent, serpent_model=args.serpent,
                    prohibition_source=src, serpent_present=bool(serp),
                    seed=seed, serpent_turns=args.serpent_turns, frame=frame,
                )
            except Exception as e:
                print(f"  ! {frame} {src} serpent={serp} seed={seed}: {type(e).__name__}: {e}", file=sys.stderr)
                f.write(json.dumps({
                    "agent_model": args.agent, "serpent_model": args.serpent,
                    "prohibition_source": src, "serpent_present": bool(serp),
                    "seed": seed, "frame": frame, "error": f"{type(e).__name__}: {e}",
                }) + "\n")
                f.flush()
                continue
            cert = certify(log.ate, log.statement)
            f.write(json.dumps({**log.to_dict(), "certification": cert.__dict__}) + "\n")
            f.flush()
            n += 1
    print(f"topped up {n}/{len(cells)} cells -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
