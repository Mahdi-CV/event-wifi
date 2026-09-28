# %% [markdown]
# # Event Capacity Test
#
# Use this notebook for real-attendee calibration. Set a unique participant ID,
# run all cells, and submit the final JSON result using the event's approved
# collection method. Do not include credentials or personal data.

# %%
import json
import os
import platform
import time
import urllib.request

PARTICIPANT_ID = os.environ.get("EVENT_PARTICIPANT_ID", "REAL-CHANGE-ME")
TEST_FILE_URL = os.environ.get("EVENT_TEST_FILE_URL", "")
started = time.perf_counter()
result = {
    "participant_id": PARTICIPANT_ID,
    "kernel_hostname": platform.node(),
    "python": platform.python_version(),
    "compute_ok": False,
    "data_access_ok": None,
    "errors": [],
}

# %%
try:
    values = [i * i for i in range(250_000)]
    result["compute_ok"] = len(values) == 250_000 and values[-1] > 0
except Exception as exc:
    result["errors"].append(f"compute: {type(exc).__name__}: {exc}")

# %%
if TEST_FILE_URL:
    try:
        with urllib.request.urlopen(TEST_FILE_URL, timeout=30) as response:
            payload = response.read()
        result["data_access_ok"] = len(payload) > 0
        result["download_bytes"] = len(payload)
    except Exception as exc:
        result["data_access_ok"] = False
        result["errors"].append(f"data: {type(exc).__name__}: {exc}")

# %%
result["total_seconds"] = time.perf_counter() - started
result["passed"] = result["compute_ok"] and result["data_access_ok"] is not False
print("EVENT_WIFI_RESULT=" + json.dumps(result, sort_keys=True))

