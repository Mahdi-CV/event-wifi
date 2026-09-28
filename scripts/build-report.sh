#!/usr/bin/env bash
set -euo pipefail

RUN_DIR=${1:?usage: build-report.sh results/<run-id>}
ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
exec "$ROOT_DIR/.venv/bin/python" -m event_wifi.report "$RUN_DIR"

