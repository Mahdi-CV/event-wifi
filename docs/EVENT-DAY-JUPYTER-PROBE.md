# Event-Day Jupyter Probe

## Recommendation

Yes, run the attendee probe during the upcoming event. It creates the real-user
baseline needed to determine whether USB-adapter automation behaves similarly to
actual attendees.

Use [the attendee probe](../notebooks/event_capacity_test.py) as cells in the
real workshop notebook. Do not give attendees a separate synthetic workload if
that causes them to behave differently from the actual workshop. The best
placement is:

1. initialization and anonymous ID at the beginning;
2. browser probe immediately after attendees open Jupyter;
3. representative computation and data access within the real workflow;
4. final result after the important workshop operations complete.

## Before the event

The event and Jupyter owners should set:

```bash
export EVENT_NAME="your-event-name"
export EVENT_TEST_FILE_URL="https://approved.example/test-data.bin"
export EVENT_RESULTS_DIRECTORY="/approved/shared/results/path"
export EVENT_DOWNLOAD_REPETITIONS="3"
```

Requirements for the test file:

- hosted on the same data path attendees will use;
- safe for every attendee to read;
- stable for the entire test;
- small enough to avoid becoming a denial-of-service workload;
- contains no credentials or private attendee data.

Test the notebook with at least two ordinary attendee accounts before the event.
Confirm they can write results without reading or overwriting other users'
files. If the shared directory cannot be secured appropriately, let each user
download or submit their own result through an approved collection method.

## During the event

1. Ask attendees to connect only the device they will use for the workshop.
2. Assign an exact synchronized start time for `Run All`.
3. Record the number of people who attempted the test.
4. Record the number who could not reach Jupyter at all; they cannot produce a
   notebook result and must be counted separately.
5. Ask attendees not to enter names or email addresses into the notebook.
6. Record venue/AP/router and Jupyter metrics using synchronized UTC time.
7. Keep help-desk notes for captive portal, SSO, browser, and device-specific
   failures.

The missing-client count matters. If 100 attendees attempt to participate but
only 92 reach the notebook, analyzing 92 successful result files alone would
overstate reliability.

## What the two result types mean

`EVENT_WIFI_BROWSER_RESULT` is produced in the attendee's browser. Its request
timings include the local device, Wi-Fi, venue network, WAN, and Jupyter web
service.

`EVENT_WIFI_RESULT` is produced by the remote Python kernel. It measures kernel
execution and server-side access to the configured data URL. It does not inspect
the attendee's local Wi-Fi adapter or DHCP lease.

The browser result currently appears in notebook output for copying or
collection through an approved event process. The kernel result is also saved as
an anonymous JSON file.

## Minimum event record

For meaningful later comparison, preserve:

- total attendees expected;
- total attendees who attempted;
- total unable to associate to Wi-Fi;
- total unable to receive DHCP;
- total unable to reach or authenticate to Jupyter;
- number of browser probe results;
- number of kernel result files;
- AP/router/Jupyter metrics and timestamps;
- exact notebook revision or Git commit;
- venue layout, AP configuration, and event start pattern.

## Comparison with automation

Compare overlapping fields:

| Real attendee | Automated client |
|---|---|
| browser HTTP success | Jupyter API reachability |
| browser request timing | API and total timing |
| kernel workload completion | workload completion |
| kernel total time | execution and total time |
| data access result | configured workload data access |
| errors | errors |

Do not expect exact timings. The purpose is to determine whether failure rates
and trends move together as concurrency increases.

## Privacy and security

- Use random `REAL-...` identifiers.
- Do not collect names, emails, cookies, tokens, or IP addresses.
- Do not expose a writable unauthenticated public collection endpoint.
- Review result JSON before sharing it outside the event team.
- Obtain event and platform-owner approval before collecting telemetry.

