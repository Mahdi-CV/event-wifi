from __future__ import annotations

import argparse
import json
import os
import random
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from .config import load_adapters, load_toml


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--adapters", required=True)
    parser.add_argument("--run-dir")
    args = parser.parse_args()

    config_path = str(Path(args.config).resolve())
    adapters_path = str(Path(args.adapters).resolve())
    config = load_toml(config_path)
    adapters = load_adapters(adapters_path)
    test = config["test"]
    token_env = config["jupyter"].get("token_env", "JUPYTER_TOKEN")
    if not os.environ.get(token_env):
        raise SystemExit(f"Required environment variable {token_env} is not set")
    concurrency = min(int(test.get("concurrency", len(adapters))), len(adapters))
    selected = adapters[:concurrency]
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = Path(args.run_dir or Path(test.get("results_root", "results")) / run_id)
    run_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "run_id": run_id,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "config": config,
        "adapters_file": adapters_path,
        "clients": [adapter.client_id for adapter in selected],
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

    failures = 0
    iterations = int(test.get("iterations", 1))
    ramp = float(test.get("ramp_seconds", 0))
    pause = float(test.get("pause_between_iterations_seconds", 0))
    python = sys.executable

    for iteration in range(1, iterations + 1):
        processes: list[tuple[str, subprocess.Popen]] = []
        launch_order = selected[:]
        random.shuffle(launch_order)
        interval = ramp / max(len(launch_order) - 1, 1)
        for index, adapter in enumerate(launch_order):
            output = run_dir / f"{adapter.client_id}-iteration-{iteration:03d}.jsonl"
            output.touch()
            command = [
                "sudo", "-n", f"--preserve-env={token_env}",
                "ip", "netns", "exec", adapter.namespace,
                python, "-m", "event_wifi.worker",
                "--config", config_path,
                "--client-id", adapter.client_id,
                "--interface", adapter.interface,
                "--iteration", str(iteration),
                "--output", str(output.resolve()),
            ]
            env = os.environ.copy()
            process = subprocess.Popen(command, env=env)
            processes.append((adapter.client_id, process))
            if index + 1 < len(launch_order) and interval:
                time.sleep(interval)
        for client_id, process in processes:
            return_code = process.wait()
            if return_code:
                failures += 1
                print(f"{client_id} iteration {iteration} failed", file=sys.stderr)
        if iteration < iterations and pause:
            time.sleep(pause)

    print(run_dir.resolve())
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
