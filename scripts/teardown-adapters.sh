#!/usr/bin/env bash
set -euo pipefail

ADAPTERS_FILE=${1:-config/adapters.toml}
ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

if [[ ${EUID} -ne 0 ]]; then
  echo "Run with sudo." >&2
  exit 1
fi

mapfile -t rows < <("$ROOT_DIR/.venv/bin/python" - "$ADAPTERS_FILE" <<'PY'
import sys, tomllib
with open(sys.argv[1], "rb") as f:
    for item in tomllib.load(f)["adapter"]:
        print("|".join([item["interface"], item["namespace"]]))
PY
)

for row in "${rows[@]}"; do
  IFS='|' read -r iface namespace <<< "$row"
  ip netns list | grep -q "^$namespace\b" || continue
  ip netns pids "$namespace" | xargs --no-run-if-empty kill || true
  ip netns exec "$namespace" ip link set "$iface" down 2>/dev/null || true
  ip netns exec "$namespace" ip link set "$iface" netns 1 2>/dev/null || true
  ip netns delete "$namespace" 2>/dev/null || true
  ip link set "$iface" up 2>/dev/null || true
  nmcli device set "$iface" managed yes 2>/dev/null || true
  echo "Restored $iface"
done

