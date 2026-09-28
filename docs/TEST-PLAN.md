# Capacity Test Plan

## Safety and change control

Obtain written venue and Jupyter-owner approval. Record the test window, stop
conditions, contacts, expected load, and rollback plan. Do not test during an
unrelated live event.

Stop immediately if:

- production users are affected;
- AP/router management becomes unavailable;
- packet loss or latency exceeds the agreed safety threshold;
- Jupyter error rate remains above the threshold for two measurement windows;
- any load generator overheats, loses power, or saturates its own resources.

## Phases

1. **Functional trial:** 1, 2, then 5 clients.
2. **Baseline:** 10 clients for at least three iterations.
3. **Progressive load:** 25, 50, 75, 100, then increments appropriate to the
   expected event size.
4. **Boundary search:** once a level fails, retest below it using smaller
   increments.
5. **Burst:** ramp from zero to the target in 60–180 seconds.
6. **Soak:** hold the intended production load for the expected workshop
   duration.
7. **Real-user calibration:** compare automated clients with attendee notebook
   results.

Repeat each level enough times to distinguish a stable limit from a transient
failure. Reset or wait for Jupyter kernels and infrastructure state to return to
baseline between levels.

## Test matrix

Record at least:

| Dimension | Values |
|---|---|
| Client count | 10, 25, 50, 75, 100, boundary increments |
| Arrival pattern | gradual, 60-second burst, 180-second burst |
| Band | mixed, 2.4 GHz, 5 GHz/6 GHz where supported |
| Location | representative seating zones and weak-signal edges |
| Workload | standard notebook, data-access workload |
| Duration | short repetitions and full-session soak |

## Pass/fail interpretation

Do not call a run a Wi-Fi failure solely because a notebook failed:

- no association, DHCP address, or default route: client/Wi-Fi/DHCP;
- HTTPS/API failed while Wi-Fi remained associated: WAN, DNS, TLS, proxy, or
  service reachability;
- API succeeded but kernel creation failed: Jupyter capacity/control plane;
- kernel started but execution failed: kernel/runtime/data dependency;
- all automated clients pass but real users fail: browser, SSO, device diversity,
  captive portal, or human-workflow difference.

The validated ceiling is the highest repeatable level meeting all criteria, not
the largest one-time successful run. Apply operational headroom before declaring
event capacity.

## Suggested result storage

Keep each run directory immutable and copy it to a central analysis location:

```text
results/
└── 20260928T180000Z/
    ├── manifest.json
    ├── AUTO-001-iteration-001.jsonl
    ├── ...
    ├── results.csv
    ├── summary.json
    └── report.md
```

Record the Git commit, AP/router configuration export, Jupyter deployment
version, room, date, and operator alongside the run. A result without those
inputs is difficult to reproduce.
