# Architecture and Data Model

Each physical adapter is moved from the host namespace into a dedicated namespace:

```text
Linux controller (management over Ethernet)
├── ew-AUTO-001 ─ wlan USB #1 ─ AP ─ Jupyter kernel #1
├── ew-AUTO-002 ─ wlan USB #2 ─ AP ─ Jupyter kernel #2
└── ew-AUTO-003 ─ wlan USB #3 ─ AP ─ Jupyter kernel #3
```

The worker captures network state before and after the workload. It then:

1. calls the Jupyter `/api` endpoint;
2. creates a kernel through `/api/kernels`;
3. opens the kernel channels WebSocket;
4. executes the configured code;
5. waits for the kernel to become idle;
6. deletes the kernel;
7. writes a single JSONL record.

One attempt records identifiers, UTC time, stage booleans, stage timings, output,
errors, IP/default-route details, interface counters, and `iw` association data.

The current report intentionally avoids inventing a disconnect count from
ambiguous symptoms. Derive explicit disconnect/reconnect events in a future
collector from `wpa_supplicant` event logs or AP-controller telemetry.

