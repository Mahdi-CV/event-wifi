# %% [markdown]
# # Event Wi-Fi and Jupyter Attendee Probe
#
# Add these cells near the beginning of the real event notebook and ask every
# attendee to use **Run All** at the same announced time.
#
# This probe deliberately does not collect names, email addresses, IP addresses,
# cookies, or credentials. Each browser session receives a random `REAL-...` ID.
#
# Important: Python cells run on the remote Jupyter kernel. They measure kernel,
# data-service, and end-to-end cell completion, but cannot directly inspect the
# attendee laptop's Wi-Fi association or DHCP state. The browser probe below
# separately measures browser-to-Jupyter HTTP requests across the attendee Wi-Fi.

# %%
import json
import os
import platform
import socket
import statistics
import time
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Configure these in the Jupyter environment or edit them for the event.
EVENT_NAME = os.environ.get("EVENT_NAME", "EVENT-CHANGE-ME")
TEST_FILE_URL = os.environ.get("EVENT_TEST_FILE_URL", "")
RESULTS_DIRECTORY = Path(os.environ.get("EVENT_RESULTS_DIRECTORY", "."))
DOWNLOAD_REPETITIONS = int(os.environ.get("EVENT_DOWNLOAD_REPETITIONS", "3"))

# Keep this anonymous. Do not replace it with an attendee's name or email.
CLIENT_ID = os.environ.get("EVENT_PARTICIPANT_ID") or f"REAL-{uuid.uuid4().hex[:8].upper()}"

run_started_monotonic = time.perf_counter()
result = {
    "schema_version": 1,
    "source": "real-attendee",
    "event_name": EVENT_NAME,
    "client_id": CLIENT_ID,
    "started_at_utc": datetime.now(timezone.utc).isoformat(),
    "kernel_hostname": platform.node(),
    "python_version": platform.python_version(),
    "dns_success": None,
    "data_access_success": None,
    "workload_completed": False,
    "download_attempts": [],
    "errors": [],
}

print(f"Anonymous test ID: {CLIENT_ID}")
print("Keep this notebook open until the final PASS/FAIL result appears.")

# %% [markdown]
# ## Browser-to-Jupyter network probe
#
# This cell runs in the browser rather than in the remote kernel. It makes five
# same-origin requests to the current Jupyter page and reports browser-observed
# latency. Save or copy its JSON result if the event team is collecting browser
# measurements.

# %%
from IPython.display import Javascript, display

display(
    Javascript(
        f"""
(async () => {{
  const result = {{
    schema_version: 1,
    source: "real-attendee-browser",
    event_name: {json.dumps(EVENT_NAME)},
    client_id: {json.dumps(CLIENT_ID)},
    started_at_utc: new Date().toISOString(),
    online_at_start: navigator.onLine,
    effective_connection_type:
      navigator.connection ? navigator.connection.effectiveType : null,
    request_milliseconds: [],
    failures: []
  }};
  for (let i = 0; i < 5; i++) {{
    const started = performance.now();
    try {{
      const response = await fetch(window.location.href, {{
        method: "GET",
        cache: "no-store",
        credentials: "same-origin"
      }});
      if (!response.ok) throw new Error(`HTTP ${{response.status}}`);
      await response.text();
      result.request_milliseconds.push(performance.now() - started);
    }} catch (error) {{
      result.failures.push(String(error));
    }}
    await new Promise(resolve => setTimeout(resolve, 500));
  }}
  result.finished_at_utc = new Date().toISOString();
  result.online_at_end = navigator.onLine;
  result.passed =
    result.request_milliseconds.length === 5 && result.failures.length === 0;
  const pre = document.createElement("pre");
  pre.style.whiteSpace = "pre-wrap";
  pre.textContent =
    "EVENT_WIFI_BROWSER_RESULT=" + JSON.stringify(result);
  element.append(pre);
}})();
"""
    )
)

# %% [markdown]
# ## Kernel and representative workload
#
# Replace or extend this deterministic calculation with the operations attendees
# will actually perform. The automated test configuration should execute the same
# logical workload.

# %%
compute_started = time.perf_counter()
try:
    values = [((i * i) % 104729) for i in range(500_000)]
    checksum = sum(values)
    result["compute_success"] = len(values) == 500_000 and checksum > 0
    result["compute_seconds"] = time.perf_counter() - compute_started
    result["compute_checksum"] = checksum
except Exception as exc:
    result["compute_success"] = False
    result["errors"].append(f"compute: {type(exc).__name__}: {exc}")

# %% [markdown]
# ## Required data access
#
# Set `EVENT_TEST_FILE_URL` to a small representative file from the same data
# path used by the workshop. Do not use a very large file: the goal is to test
# the real dependency, not to overwhelm the venue WAN.

# %%
if TEST_FILE_URL:
    parsed = urllib.parse.urlparse(TEST_FILE_URL)
    try:
        dns_started = time.perf_counter()
        socket.getaddrinfo(parsed.hostname, parsed.port or 443)
        result["dns_success"] = True
        result["dns_seconds"] = time.perf_counter() - dns_started
    except Exception as exc:
        result["dns_success"] = False
        result["errors"].append(f"dns: {type(exc).__name__}: {exc}")

    for attempt in range(1, DOWNLOAD_REPETITIONS + 1):
        download = {"attempt": attempt}
        started = time.perf_counter()
        try:
            request = urllib.request.Request(
                TEST_FILE_URL,
                headers={"User-Agent": "event-wifi-attendee-probe/1"},
            )
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = response.read()
                download["http_status"] = response.status
            download["success"] = len(payload) > 0
            download["bytes"] = len(payload)
        except Exception as exc:
            download["success"] = False
            download["error"] = f"{type(exc).__name__}: {exc}"
            result["errors"].append(
                f"download attempt {attempt}: {download['error']}"
            )
        download["seconds"] = time.perf_counter() - started
        result["download_attempts"].append(download)

    successful_downloads = [
        item for item in result["download_attempts"] if item["success"]
    ]
    result["data_access_success"] = (
        len(successful_downloads) == DOWNLOAD_REPETITIONS
    )
    if successful_downloads:
        durations = [item["seconds"] for item in successful_downloads]
        result["download_median_seconds"] = statistics.median(durations)
        result["download_max_seconds"] = max(durations)
else:
    result["errors"].append(
        "EVENT_TEST_FILE_URL is not configured; data access was not tested"
    )

# %% [markdown]
# ## Final result
#
# The JSON file is written into the configured results directory. In a
# multi-user Jupyter service, choose a directory that each attendee can write to
# without being able to overwrite another attendee's result.

# %%
result["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
result["total_seconds"] = time.perf_counter() - run_started_monotonic
result["workload_completed"] = bool(
    result.get("compute_success")
    and result.get("data_access_success")
    and not result["errors"]
)
result["overall_result"] = "PASS" if result["workload_completed"] else "FAIL"

RESULTS_DIRECTORY.mkdir(parents=True, exist_ok=True)
result_path = RESULTS_DIRECTORY / f"event-wifi-{CLIENT_ID}.json"
result_path.write_text(json.dumps(result, indent=2, sort_keys=True))

print("EVENT_WIFI_RESULT=" + json.dumps(result, sort_keys=True))
print(f"Saved result: {result_path}")
print(f"OVERALL RESULT: {result['overall_result']}")
