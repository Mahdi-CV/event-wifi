from __future__ import annotations

import argparse
import json
import socket
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from .config import jupyter_url, load_toml, required_token
from .jupyter_probe import run_probe


def command(command: list[str]) -> tuple[int, str]:
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    return result.returncode, result.stdout.strip()


def interface_snapshot(interface: str) -> dict:
    _, address = command(["ip", "-j", "address", "show", "dev", interface])
    _, link = command(["ip", "-j", "-s", "link", "show", "dev", interface])
    _, route = command(["ip", "-j", "route", "show", "default"])
    _, wireless = command(["iw", "dev", interface, "link"])
    return {
        "address": json.loads(address) if address else [],
        "link": json.loads(link) if link else [],
        "default_route": json.loads(route) if route else [],
        "wireless": wireless,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--client-id", required=True)
    parser.add_argument("--interface", required=True)
    parser.add_argument("--iteration", type=int, required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    config = load_toml(args.config)
    test = config["test"]
    jupyter = config["jupyter"]
    before = interface_snapshot(args.interface)
    wifi_connected = "Connected to " in before["wireless"]
    dhcp_acquired = any(
        address.get("addr_info")
        for address in before["address"]
        if address.get("ifname") == args.interface
    )
    result = run_probe(
        base_url=jupyter_url(config),
        token=required_token(config),
        kernel_name=jupyter.get("kernel_name", "python3"),
        code=config["workload"]["code"],
        request_timeout=float(test.get("request_timeout_seconds", 30)),
        kernel_timeout=float(test.get("kernel_timeout_seconds", 60)),
        execution_timeout=float(test.get("execution_timeout_seconds", 120)),
        verify_tls=bool(jupyter.get("verify_tls", True)),
    )
    after = interface_snapshot(args.interface)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "controller_id": test.get("controller_id", socket.gethostname()),
        "client_id": args.client_id,
        "interface": args.interface,
        "iteration": args.iteration,
        "wifi_connected": wifi_connected,
        "dhcp_acquired": dhcp_acquired,
        "reachable": result.reachable,
        "kernel_started": result.kernel_started,
        "workload_completed": result.workload_completed,
        "kernel_start_seconds": result.kernel_start_seconds,
        "execution_seconds": result.execution_seconds,
        "total_seconds": result.total_seconds,
        "outputs": result.outputs,
        "errors": result.errors,
        "network_before": before,
        "network_after": after,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, sort_keys=True) + "\n")
    print(json.dumps(record, indent=2))
    return 0 if result.workload_completed else 1


if __name__ == "__main__":
    raise SystemExit(main())
