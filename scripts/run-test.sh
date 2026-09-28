#!/usr/bin/env bash
set -euo pipefail

CONFIG=${1:-config/lab.toml}
ADAPTERS=${2:-config/adapters.toml}
ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

if [[ ! -x "$ROOT_DIR/.venv/bin/python" ]]; then
  echo "Missing .venv; run ./scripts/bootstrap-controller.sh first." >&2
  exit 1
fi
sudo -v
exec "$ROOT_DIR/.venv/bin/python" -m event_wifi.runner \
  --config "$CONFIG" --adapters "$ADAPTERS"

