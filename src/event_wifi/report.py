from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


def percentile(values: list[float], percent: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    rank = (len(ordered) - 1) * percent
    low = math.floor(rank)
    high = math.ceil(rank)
    if low == high:
        return ordered[low]
    return ordered[low] + (ordered[high] - ordered[low]) * (rank - low)


def pct(count: int, total: int) -> float:
    return 100.0 * count / total if total else 0.0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir")
    args = parser.parse_args()
    run_dir = Path(args.run_dir)
    records = []
    for path in sorted(run_dir.glob("*.jsonl")):
        for line in path.read_text().splitlines():
            if line.strip():
                records.append(json.loads(line))
    if not records:
        raise SystemExit(f"No JSONL results found in {run_dir}")

    total = len(records)
    wifi = sum(bool(row.get("wifi_connected")) for row in records)
    dhcp = sum(bool(row.get("dhcp_acquired")) for row in records)
    reachable = sum(bool(row["reachable"]) for row in records)
    kernels = sum(bool(row["kernel_started"]) for row in records)
    completed = sum(bool(row["workload_completed"]) for row in records)
    times = [
        float(row["total_seconds"])
        for row in records
        if row["workload_completed"] and row["total_seconds"] is not None
    ]
    summary = {
        "attempts": total,
        "unique_clients": len({row["client_id"] for row in records}),
        "wifi_connected": wifi,
        "wifi_success_percent": pct(wifi, total),
        "dhcp_acquired": dhcp,
        "dhcp_success_percent": pct(dhcp, total),
        "reachable": reachable,
        "reachable_percent": pct(reachable, total),
        "kernels_started": kernels,
        "kernel_success_percent": pct(kernels, total),
        "workloads_completed": completed,
        "workload_success_percent": pct(completed, total),
        "median_total_seconds": percentile(times, 0.50),
        "p95_total_seconds": percentile(times, 0.95),
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2))

    with (run_dir / "results.csv").open("w", newline="") as handle:
        fields = [
            "timestamp", "controller_id", "client_id", "interface", "iteration",
            "wifi_connected", "dhcp_acquired", "reachable", "kernel_started",
            "workload_completed",
            "kernel_start_seconds", "execution_seconds", "total_seconds", "errors",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in records:
            writer.writerow({key: json.dumps(row.get(key)) if key == "errors" else row.get(key) for key in fields})

    def number(value: float | None) -> str:
        return "n/a" if value is None else f"{value:.2f}"

    manifest_path = run_dir / "manifest.json"
    acceptance = {}
    if manifest_path.exists():
        acceptance = json.loads(manifest_path.read_text()).get("config", {}).get(
            "acceptance", {}
        )
    checks = {
        "Wi-Fi association": summary["wifi_success_percent"]
        >= float(acceptance.get("wifi_success_percent", 0)),
        "Jupyter reachability": summary["reachable_percent"]
        >= float(acceptance.get("jupyter_reachable_percent", 0)),
        "Kernel startup": summary["kernel_success_percent"]
        >= float(acceptance.get("kernel_success_percent", 0)),
        "Workload completion": summary["workload_success_percent"]
        >= float(acceptance.get("workload_success_percent", 0)),
        "P95 completion time": summary["p95_total_seconds"] is not None
        and summary["p95_total_seconds"]
        <= float(acceptance.get("max_p95_total_seconds", float("inf"))),
    }
    overall_pass = all(checks.values())
    summary["acceptance_checks"] = checks
    summary["overall_result"] = "PASS" if overall_pass else "FAIL"
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2))

    markdown = f"""# Event Wi-Fi Capacity Test Report

| Metric | Result |
|---|---:|
| Unique automated clients | {summary['unique_clients']} |
| Total workload attempts | {total} |
| Wi-Fi associated | {wifi} ({summary['wifi_success_percent']:.2f}%) |
| DHCP acquired | {dhcp} ({summary['dhcp_success_percent']:.2f}%) |
| Jupyter reachable | {reachable} ({summary['reachable_percent']:.2f}%) |
| Kernels started | {kernels} ({summary['kernel_success_percent']:.2f}%) |
| Workloads completed | {completed} ({summary['workload_success_percent']:.2f}%) |
| Median total time | {number(summary['median_total_seconds'])} s |
| P95 total time | {number(summary['p95_total_seconds'])} s |
| **Overall result** | **{summary['overall_result']}** |

## Acceptance checks

"""
    for label, passed in checks.items():
        markdown += f"- {label}: {'PASS' if passed else 'FAIL'}\n"
    markdown += """

## Failed attempts

"""
    failed = [row for row in records if not row["workload_completed"]]
    if failed:
        for row in failed:
            markdown += f"- `{row['client_id']}` iteration {row['iteration']}: " + (
                "; ".join(row["errors"]) or "unknown failure"
            ) + "\n"
    else:
        markdown += "None.\n"
    (run_dir / "report.md").write_text(markdown)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
