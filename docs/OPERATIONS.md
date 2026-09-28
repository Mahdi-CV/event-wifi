# Operations Runbook

## 1. Before buying hardware

Run a small proof of concept with one laptop and two known Linux-compatible USB
adapters. Confirm:

- the adapters can associate simultaneously;
- each adapter can be moved into a network namespace;
- drivers remain stable under sustained use;
- the powered hub supplies enough current;
- the Jupyter administrator can provide a supported test token/account;
- the venue authorizes active capacity testing.

Prefer adapters whose Linux chipset/driver is known before purchasing dozens.
Avoid assuming that a product name identifies the chipset; vendors sometimes
change chipsets without changing retail branding.

## 2. Controller prerequisites

- Ubuntu/Debian Linux
- wired Ethernet management connection
- five or fewer adapters for the first trial
- powered USB hub
- synchronized clock
- enough file space for results

Never use one of the test Wi-Fi interfaces for SSH management. Moving it into a
namespace will remove it from the host network stack.

## 3. Configure a laptop

```bash
./scripts/bootstrap-controller.sh
./scripts/inventory-adapters.sh
cp config/adapters.example.toml config/adapters.toml
cp config/lab.example.toml config/lab.toml
cp config/wifi.env.example config/wifi.env
chmod 600 config/wifi.env
```

Give each controller and client globally unique IDs:

```text
LAPTOP-01 / AUTO-001 through AUTO-005
LAPTOP-02 / AUTO-006 through AUTO-010
```

Copy the same `lab.toml` to every controller. Set the controller ID separately.
Do not copy result files between machines while a run is active.

## 4. Prepare adapters

```bash
sudo ./scripts/setup-adapters.sh config/adapters.toml config/wifi.env
sudo ip netns list
sudo ip netns exec ew-AUTO-001 iw dev wlx001122334401 link
sudo ip netns exec ew-AUTO-001 curl -fsS https://jupyter.example.com/api
```

The unauthenticated API check may return HTTP 403; that still proves DNS,
routing, TLS, and HTTP reachability.

## 5. Run

```bash
export JUPYTER_TOKEN='temporary-test-token'
./scripts/run-test.sh config/lab.toml config/adapters.toml
./scripts/build-report.sh results/<run-id>
```

The runner asks `sudo` to refresh credentials, then uses non-interactive
namespace execution. It preserves only the configured token environment
variable across that boundary. It creates one result file per client and
iteration, which avoids concurrent file-write corruption.

## 6. Tear down

```bash
sudo ./scripts/teardown-adapters.sh config/adapters.toml
```

Do this before unplugging adapters. If a run is interrupted, teardown is safe to
run again.

## 7. Capture venue infrastructure data

At each test level, separately export or photograph:

- AP/controller client count and radio utilization
- channel, channel width, transmit power, and band
- DHCP pool utilization and lease timing
- router CPU, memory, NAT/session-table utilization
- WAN latency, packet loss, and available bandwidth
- Jupyter proxy, hub, scheduler, kernel, CPU, memory, and error metrics
- room layout and approximate client/AP positions
- firmware and configuration versions

Use synchronized UTC timestamps so infrastructure metrics can be correlated
with JSONL results.

## 8. Authentication

The harness supports Jupyter token authentication. For OIDC/SAML or other
browser-only authentication, use a dedicated supported test mechanism from the
service owner. Do not automate personal MFA, store session cookies in the repo,
or disable TLS verification outside a controlled lab.

## 9. Multi-laptop synchronization

For a burst, start all controllers against an agreed UTC time:

```bash
sleep "$(( $(date -d '2026-10-01 18:00:00 UTC' +%s) - $(date +%s) ))"
./scripts/run-test.sh config/lab.toml
```

For production use, wrap this in an operator script and reject negative sleep
values. Verify clocks with `timedatectl` before every test.
