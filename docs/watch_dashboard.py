"""Rebuild the dashboard whenever a run writes to logs/.

Polls mtimes rather than using filesystem events: experiments append to JSONL
continuously, so event-driven rebuilds would fire hundreds of times per run. A
debounce interval means the page settles to "current" a few seconds after a run
stops writing, which is what you actually want when you glance at it.

  python docs/watch_dashboard.py            # 20s poll, rebuild on change
  python docs/watch_dashboard.py 60         # slower poll
"""
import glob
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "docs", "build_dashboard.py")
POLL = int(sys.argv[1]) if len(sys.argv) > 1 else 20
DEBOUNCE = 10          # wait for writes to settle before rebuilding


def fingerprint():
    """Cheap change signal: (path, size, mtime) over every episode log."""
    out = []
    for p in sorted(glob.glob(os.path.join(ROOT, "logs", "*.jsonl"))):
        try:
            st = os.stat(p)
            out.append((p, st.st_size, int(st.st_mtime)))
        except OSError:
            pass
    return tuple(out)


def build():
    r = subprocess.run([sys.executable, BUILD], capture_output=True, text=True)
    line = (r.stdout or r.stderr or "").strip().splitlines()
    print(f"[{time.strftime('%H:%M:%S')}] {line[-1] if line else 'rebuilt'}", flush=True)


print(f"watching logs/ every {POLL}s (debounce {DEBOUNCE}s) — Ctrl-C to stop", flush=True)
build()
last = fingerprint()
pending_since = None

while True:
    time.sleep(POLL)
    now = fingerprint()
    if now != last:
        last = now
        pending_since = time.time()          # something moved; wait for quiet
        continue
    if pending_since and time.time() - pending_since >= DEBOUNCE:
        build()
        pending_since = None
