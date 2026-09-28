from __future__ import annotations

import argparse

from . import report, runner, worker


def main() -> int:
    parser = argparse.ArgumentParser(prog="event-wifi")
    parser.add_argument("command", choices=["run", "worker", "report"])
    args, remaining = parser.parse_known_args()
    import sys
    sys.argv = [sys.argv[0], *remaining]
    return {"run": runner.main, "worker": worker.main, "report": report.main}[args.command]()

