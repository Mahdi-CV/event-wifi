# Event Wi-Fi and Jupyter Capacity Validation Implementation Plan

## Executive summary

Events with 100–200 attendees have experienced major interruptions because the
venue Wi-Fi infrastructure was not proven to support the number of simultaneous
connections and the actual remote Jupyter workload.

This project creates a repeatable pre-event validation system. Linux laptops
equipped with multiple USB Wi-Fi adapters act as independent attendees. Each
adapter connects to the event Wi-Fi, receives its own DHCP lease, reaches the
remote Jupyter service, starts a kernel, executes the event workload, and records
the result.

The project changes the readiness decision from:

> “We saw 100 devices connected.”

to:

> “We validated that 100 concurrent event users could connect through the
> deployed Wi-Fi infrastructure and complete the actual remote Jupyter workload
> within the agreed reliability and performance thresholds.”

## Objective

Determine the maximum number of concurrent attendees who can reliably complete
this path:

```text
Connect to event Wi-Fi
        ↓
Receive a DHCP address and working route
        ↓
Reach and authenticate to remote Jupyter
        ↓
Create a kernel
        ↓
Execute the standard event workload
        ↓
Access required data
        ↓
Complete within the performance target
```

The final outcome is a documented, repeatable concurrent-user ceiling for a
specific venue, network configuration, Jupyter deployment, and workload.

## Success criteria

The initial recommended thresholds are:

| Stage | Requirement |
|---|---:|
| Wi-Fi association | at least 98% |
| DHCP and route acquisition | at least 98% |
| Jupyter reachability | at least 98% |
| Kernel startup | at least 98% |
| Workload completion | at least 98% |
| Unexpected disconnects | less than 1% |
| P95 completion time | within the agreed event target |
| Infrastructure stability | no AP, router, WAN, or Jupyter instability |

These values are configurable. The stakeholders responsible for the venue
network, Jupyter environment, and event must approve the final values before
capacity testing begins.

## Scope

### Included

- Linux load-generator laptop preparation
- one independent Wi-Fi station per supported USB adapter
- Wi-Fi association, DHCP, routing, DNS, HTTPS, and WebSocket testing
- Jupyter API access, kernel creation, execution, and cleanup
- gradual, burst, boundary, and soak testing
- standardized real-attendee notebook calibration
- per-attempt JSONL data, aggregate CSV, JSON summary, and Markdown report
- correlation guidance for AP/router and Jupyter platform telemetry

### Not included

- redesigning or installing the venue's production Wi-Fi
- bypassing captive portals, SSO, MFA, or security controls
- automatically collecting proprietary AP/controller metrics
- browser rendering and UI performance automation
- purchasing hardware without first validating chipset and driver compatibility
- claiming that automated USB clients perfectly represent all attendee devices

## Target architecture

```text
                         Remote Jupyter platform
                      proxy / hub / kernels / data
                                  |
                              Internet/WAN
                                  |
                         Venue router and DHCP
                                  |
                     Venue access points / radios
                           /          |          \
                    Laptop 1      Laptop 2      Laptop N
                    wired mgmt    wired mgmt    wired mgmt
                    5 adapters    5 adapters    5 adapters
                    5 clients     5 clients     5 clients
```

Initial scale:

```text
10 laptops × approximately 5 adapters = approximately 50 clients
```

Target scale:

```text
20 laptops × approximately 5 adapters = approximately 100 clients
```

The number of stable adapters per laptop must be demonstrated in the pilot. USB
power, USB controller sharing, driver stability, CPU, and memory can make five
adapters per laptop too many or unnecessarily conservative.

## Workstreams and deliverables

### 1. Requirements and authorization

Deliverables:

- event workload definition
- approved reliability and latency thresholds
- authorized test window and stop conditions
- venue network and Jupyter owner contacts
- expected event size and desired safety margin
- decision on Jupyter test authentication

Exit gate: all owners agree on what constitutes a passing test.

### 2. Hardware proof of concept

Start with one Linux laptop, one powered USB hub, and two USB Wi-Fi adapters.

Deliverables:

- confirmed Linux chipset and driver compatibility
- simultaneous association from isolated adapters
- stable powered-hub operation
- wired management path
- adapter inventory with interface names and MAC addresses

Exit gate: two independent clients complete repeated workloads without
load-generator instability.

### 3. Jupyter workload validation

Deliverables:

- dedicated, least-privilege test credential
- representative and deterministic workload
- required test data available
- confirmed kernel name and API path
- agreed cleanup behavior and platform monitoring
- real-attendee calibration notebook

Exit gate: one automated client and one real browser user produce comparable
successful workload results.

### 4. Controller image and configuration

Deliverables:

- controller bootstrap completed
- unique controller and client identifiers assigned
- local adapter inventory configured
- secrets stored outside Git
- clocks synchronized
- test configuration copied consistently across controllers

Exit gate: every controller passes a five-client functional test.

### 5. Venue baseline

Capture:

- AP placement, channels, widths, bands, and transmit power
- client limits and radio utilization
- DHCP pool and lease settings
- router CPU, memory, and NAT/session capacity
- WAN bandwidth, latency, and loss
- Jupyter deployment version, capacity, and baseline metrics
- room layout and test-client positions

Exit gate: all infrastructure observations use synchronized timestamps and can
be correlated with client results.

### 6. Capacity execution

Run the following sequence:

1. Functional: 1, 2, and 5 clients.
2. Baseline: 10 clients for at least three iterations.
3. Progressive: 25, 50, 75, 100, and additional expected levels.
4. Boundary: smaller increments around the first failing level.
5. Burst: zero to target load within 60–180 seconds.
6. Soak: target production load for the expected workshop duration.
7. Calibration: automated and real attendees operating together.

Exit gate: the boundary has repeatable passing and failing levels, rather than a
single anomalous result.

### 7. Analysis and readiness decision

Deliverables:

- immutable result directories from every run
- stage success rates and completion latency percentiles
- classified Wi-Fi, WAN, Jupyter control-plane, and workload failures
- automated-versus-real-user comparison
- maximum validated concurrent workload
- recommended operational capacity with headroom
- remediation list and retest requirements

Exit gate: event owners approve a clear go, conditional-go, or no-go decision.

## Responsibility model

One person may fill multiple roles, but every responsibility should be assigned.

| Role | Responsibility |
|---|---|
| Test lead | plan, schedule, safety, execution, final report |
| Network owner | AP/router/DHCP access, metrics, configuration, rollback |
| Jupyter owner | credentials, quotas, service metrics, kernel cleanup |
| Controller operator | laptop setup, adapter inventory, run execution |
| Event owner | workload approval, attendee target, acceptance criteria |
| Observer/data lead | timestamped notes, infrastructure data, result archive |

## Data captured

Every automated attempt records:

- UTC timestamp, controller, client, interface, and iteration
- association state and Wi-Fi link information
- IP address, default route, and interface counters
- Jupyter endpoint reachability
- kernel creation result and latency
- workload result and latency
- total completion time
- kernel output and errors
- network state before and after execution

Separately capture AP/controller, DHCP, router, WAN, and Jupyter platform metrics.
Do not place credentials or attendee personal information in result files.

## Determining the validated ceiling

For each load level:

1. Run enough repetitions to evaluate consistency.
2. Verify all agreed stage thresholds.
3. Check P95 completion time.
4. Confirm the load generators did not become the bottleneck.
5. Confirm the venue and Jupyter infrastructure remained stable.
6. Classify failures by layer.

The validated ceiling is the highest repeatable concurrent level that satisfies
all criteria. The production recommendation must be lower than that ceiling.
Record the selected headroom and why it is appropriate.

Example:

```text
50 clients     PASS
75 clients     PASS
100 clients    PASS
125 clients    FAIL
110 clients    PASS
120 clients    FAIL
115 clients    PASS

Validated test ceiling: 115 concurrent clients
Operational event target after approved headroom: lower than 115
```

## Risks and controls

| Risk | Control |
|---|---|
| Incompatible adapter chipset | prove the exact model/revision before bulk purchase |
| Underpowered USB hubs | use powered hubs and monitor resets/errors |
| Laptop becomes bottleneck | monitor controller CPU, memory, USB, and process failures |
| Test differs from attendee behavior | calibrate against real users and browser workflow |
| SSO cannot be automated safely | use a supported test token/account from the service owner |
| Venue radio conditions change | test in the actual room and document layout/interference |
| Jupyter is the bottleneck | correlate kernel/proxy/platform metrics with client results |
| Test disrupts production | authorization, isolated window, stop conditions, rollback |
| Results cannot be reproduced | preserve config versions, Git commit, timestamps, and artifacts |
| Device count is mistaken for capacity | require successful end-to-end workload completion |

## Definition of done

The project is complete for a venue/event configuration when:

- the scripts run successfully on all controller laptops;
- all physical adapters are inventoried and uniquely identified;
- the standard automated workload and real-attendee notebook are approved;
- secrets remain outside the repository and result archive;
- progressive, burst, soak, and calibration tests are complete;
- failures are classified by infrastructure layer;
- results include median and P95 latency plus stage success rates;
- a repeatable maximum concurrent-user ceiling is established;
- an operational attendee target with documented headroom is approved;
- the report includes the Git commit and relevant network/Jupyter versions;
- unresolved risks and required remediation are assigned to owners.

## Immediate next actions

1. Name the test lead, network owner, Jupyter owner, and event owner.
2. Agree on the real event notebook workload and P95 completion target.
3. Obtain a dedicated Jupyter test account/token.
4. Buy or borrow two candidate adapters and one powered hub.
5. Run the two-adapter proof of concept.
6. Select hardware only after the proof of concept passes.
7. Schedule a venue test window and baseline infrastructure capture.
8. Scale gradually; do not begin with 50 or 100 clients.

## Related documents

- [Operations runbook](OPERATIONS.md)
- [Detailed capacity test procedure](TEST-PLAN.md)
- [Architecture and data model](ARCHITECTURE.md)
- [Repository quick start](../README.md)
