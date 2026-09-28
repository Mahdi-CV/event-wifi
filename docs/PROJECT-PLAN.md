# Automated Event Wi-Fi & Jupyter Capacity Validation Plan

## Objective

Determine the maximum number of concurrent event attendees who can reliably:

**Connect to event Wi-Fi → reach our remote Jupyter environment → launch a notebook → execute the required workload successfully.**

The automated test will reproduce the same workflow as real attendees and establish a validated concurrent-user ceiling.

---

## Test Architecture

```text
                Remote Jupyter Server
                        |
                     Internet
                        |
                 Event Router
                        |
                Bridges / APs
                  /    |    \
             Laptop  Laptop  Laptop
                |       |       |
             USB Wi-Fi adapters
             acting as independent
                 test users
```

### Initial Scale

```text
10 laptops × 5 USB Wi-Fi adapters
≈ 50 concurrent users
```

Scale to:

```text
20 laptops × 5 adapters
≈ 100 concurrent users
```

Each USB adapter represents one independent Wi-Fi client with its own:

- MAC address
- Wi-Fi association
- DHCP/IP address
- connection to the remote Jupyter environment

---

# Required Equipment

### Existing

- Event router
- Wireless bridges/access points
- Existing laptops
- Remote Jupyter environment

### Purchase

For 50 automated clients:

| Item | Qty |
|---|---:|
| USB Wi-Fi adapters | 50 |
| Powered USB hubs | 10 |
| Ethernet cables for laptop management | 10 |
| Power strips/extensions | As needed |

For 100 clients:

| Item | Qty |
|---|---:|
| USB Wi-Fi adapters | 100 |
| Powered USB hubs | 20 |
| Test laptops | ~20 |

A mix of 2.4 GHz and 5 GHz adapters is preferred to better represent real attendee devices.

---

# Standard Jupyter Test Notebook

A dedicated **Event Capacity Test Notebook** will be available in the remote Jupyter environment.

Both real attendees and automated clients will execute the same notebook/workload.

The notebook will perform the actual operations expected during the event and record:

1. Jupyter environment reached successfully
2. Notebook opened successfully
3. Kernel started successfully
4. Test cells executed successfully
5. Data/file access completed
6. Execution latency
7. Total notebook completion time
8. Kernel disconnects/reconnects
9. Errors/timeouts
10. Overall PASS/FAIL

Example result:

```text
Client ID: AUTO-042

Jupyter Reachable: PASS
Kernel Start: 3.2 sec
Notebook Execution: PASS
Execution Time: 18.4 sec
Data Transfer: PASS
Reconnects: 0
Errors: 0

RESULT: PASS
```

---

# Automated User Workflow

Each automated Wi-Fi client will execute the same sequence:

```text
Connect to Event Wi-Fi
        ↓
Receive DHCP address
        ↓
Connect to remote Jupyter service
        ↓
Open test notebook/session
        ↓
Start kernel
        ↓
Execute defined notebook workload
        ↓
Record completion/error/timing
        ↓
Repeat at defined interval
```

Rather than generating arbitrary traffic such as continuous downloads, the automated clients generate the **actual application traffic expected at the event**.

This provides a much more meaningful capacity measurement.

---

# Real Attendee Validation

During the scheduled in-person session, attendees will:

```text
1. Connect to event Wi-Fi
2. Open the remote Jupyter environment
3. Open the Event Capacity Test Notebook
4. Run All
5. Complete the normal event workflow
```

The notebook records standardized workload results.

Real attendees are tagged:

```text
REAL-001
REAL-002
REAL-003
...
```

Automated clients are tagged:

```text
AUTO-001
AUTO-002
AUTO-003
...
```

This allows direct comparison between real-user and automated behavior.

---

# Important Client-Side Measurement

Because Jupyter kernels execute on the remote server, notebook code primarily measures the **remote Jupyter workload**, not the attendee's local Wi-Fi interface.

Therefore the automated test system should additionally record locally:

```text
Wi-Fi connection success
DHCP success
Client disconnect/reconnect
Connection to Jupyter endpoint
HTTP/WebSocket failures
```

These measurements will be correlated with notebook results.

This separates:

**Wi-Fi/network failure**

from:

**Jupyter/server workload failure**

---

# Capacity Test

Clients are added progressively:

```text
10 users
25 users
50 users
75 users
100 users
125 users
...
```

At every level, all clients execute the same Jupyter workload.

Example:

```text
50 clients:

49 reached Jupyter
49 kernels started
48 notebooks completed
1 kernel timeout
1 client Wi-Fi disconnect

Completion rate = 96%
```

---

# Determining the Concurrent-User Ceiling

The validated ceiling is:

> **The highest number of concurrent clients at which the required Jupyter workload continues to meet the agreed reliability and performance requirements.**

Example acceptance criteria:

```text
Wi-Fi association success       ≥ 98%
Jupyter reachability            ≥ 98%
Kernel startup success          ≥ 98%
Notebook completion             ≥ 98%
Unexpected disconnects          < 1%
Notebook completion time        within agreed threshold
No router/bridge instability
```

Example capacity test:

```text
50 users       PASS
75 users       PASS
100 users      PASS
125 users      FAIL
```

Additional testing:

```text
110 users      PASS
120 users      FAIL
115 users      PASS
```

### Validated Capacity

```text
Maximum validated concurrent workload:
115 Jupyter users
```

The production event should operate below this ceiling to maintain capacity headroom.

---

# Burst Test

Events may have many users joining simultaneously.

Example:

```text
0 → 50 users connecting and launching Jupyter
within 60 seconds
```

and:

```text
0 → 100 users
within 2–3 minutes
```

Measure:

- Wi-Fi association
- DHCP response
- Jupyter login/access
- server/session creation
- kernel startup
- notebook execution
- failures/timeouts

This tests the actual attendee arrival scenario.

---

# Real vs. Automated Calibration

Initial in-person testing provides the baseline.

Example:

| Metric | Automated | Real Users |
|---|---:|---:|
| Jupyter reachability | 100% | 98% |
| Kernel success | 98% | 98% |
| Notebook completion | 98% | 96% |
| Median completion | 21 sec | 23 sec |
| Disconnects | 1 | 2 |

If the automated results closely track real-user behavior, the automated environment can then be reused for future:

- router testing
- bridge testing
- AP changes
- firmware upgrades
- configuration changes
- pre-event capacity validation

---

# Final Deliverable

At the end of every test:

```text
Concurrent users tested:       100

Wi-Fi connected:                99
Reached Jupyter:                99
Kernels started:                98
Notebook completed:             98

Median notebook time:         21.4 sec
P95 notebook time:            37.2 sec

Network disconnects:             1
Kernel failures:                  1

OVERALL RESULT: PASS

Validated capacity: ≥100 concurrent Jupyter users
```

## End Goal

Move from:

> “We had 100 devices connected.”

to:

> **“We validated that 100 concurrent event users can connect over the deployed Wi-Fi infrastructure and successfully execute the actual remote Jupyter workload within defined reliability and performance thresholds.”**

## Implementation companion

The repository's [implementation plan](IMPLEMENTATION-PLAN.md) translates this
validation plan into workstreams, owners, decision gates, risks, immediate next
actions, and a definition of done.
