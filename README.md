# Event Wi-Fi Capacity Validator

Repeatable validation of the complete attendee path:

```text
USB Wi-Fi client -> event AP/DHCP -> Internet -> remote Jupyter
                  -> kernel start -> workload execution -> result capture
```

The project turns Linux laptops with multiple USB Wi-Fi adapters into independent
test clients. Each adapter is placed in a separate Linux network namespace, so it
has its own Wi-Fi association, MAC address, DHCP lease, routing table, HTTPS
connection, Jupyter kernel, and WebSocket.

## What this validates

- Wi-Fi association and DHCP success per adapter
- DNS/HTTPS reachability from each adapter's network namespace
- Jupyter API authentication and kernel creation
- Jupyter WebSocket stability and code execution
- Workload latency, failures, interface counters, and disconnect symptoms
- Progressive and burst tests with machine-readable and Markdown reports

## Important limitations

- One physical Wi-Fi adapter normally represents one associated station. Adding
  IP addresses or browser tabs does **not** emulate additional Wi-Fi clients.
- The automated workload exercises Jupyter's API and kernel channel, not browser
  rendering or an interactive SSO page. If your service requires SSO, obtain a
  supported API token or test credential from the Jupyter administrator.
- USB bus bandwidth/power and laptop CPU can become bottlenecks. Use powered
  hubs, spread adapters across USB controllers, and monitor the load generator.
- Only test networks and services you own or are explicitly authorized to test.

## Quick start

Supported controller: Ubuntu/Debian Linux with `systemd`, `iproute2`, `iw`,
`wpa_supplicant`, and a DHCP client.

```bash
./scripts/bootstrap-controller.sh
cp config/lab.example.toml config/lab.toml
cp config/adapters.example.toml config/adapters.toml
```

Edit both files, then keep the laptop's management connection on Ethernet and
run:

```bash
sudo ./scripts/setup-adapters.sh config/adapters.toml config/wifi.env
export JUPYTER_TOKEN='replace-with-a-test-token'
./scripts/run-test.sh config/lab.toml
./scripts/build-report.sh results/<run-id>
sudo ./scripts/teardown-adapters.sh config/adapters.toml
```

Do not put Wi-Fi passwords, Jupyter tokens, or cookies in Git. `config/wifi.env`
and `config/*.local.toml` are ignored.

## Repository map

| Path | Purpose |
|---|---|
| `config/` | Test and adapter inventory examples |
| `scripts/` | Laptop setup, execution, capture, and reporting |
| `src/event_wifi/` | Jupyter client, orchestration, and report code |
| `notebooks/` | Human attendee calibration notebook |
| `docs/` | Deployment, test, and interpretation runbooks |
| `tests/` | Offline unit tests |

Start with the canonical
[Automated Event Wi-Fi & Jupyter Capacity Validation Plan](docs/PROJECT-PLAN.md).
The [implementation plan](docs/IMPLEMENTATION-PLAN.md) adds workstreams,
responsibilities, risks, decision gates, immediate next actions, and the
definition of done. Then follow the [operations runbook](docs/OPERATIONS.md)
and [detailed test plan](docs/TEST-PLAN.md). For a live event, use the
[event-day Jupyter probe guide](docs/EVENT-DAY-JUPYTER-PROBE.md).

The canonical repository is hosted under `Mahdi-CV/event-wifi`. Keep it private
if venue topology, internal Jupyter URLs, or test results will be tracked.
Secrets must remain outside Git even in a private repository.

## Recommended acceptance criteria

Set these to match the event's service-level objective:

```text
Wi-Fi/DHCP success         >= 98%
Jupyter reachable          >= 98%
Kernel startup             >= 98%
Workload completion        >= 98%
Unexpected disconnects      < 1%
P95 completion time        <= agreed threshold
```

The production attendee target should remain below the measured ceiling. A
common planning choice is 20–30% headroom, but the final margin should reflect
event criticality, RF variability, and whether attendees carry multiple devices.
