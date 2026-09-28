#!/usr/bin/env bash
set -euo pipefail

ADAPTERS_FILE=${1:-config/adapters.toml}
WIFI_ENV=${2:-config/wifi.env}
ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

if [[ ${EUID} -ne 0 ]]; then
  echo "Run with sudo." >&2
  exit 1
fi
if [[ ! -f "$WIFI_ENV" ]]; then
  echo "Missing $WIFI_ENV; copy config/wifi.env.example and chmod 600." >&2
  exit 1
fi

set -a
source "$WIFI_ENV"
set +a
: "${WIFI_SSID:?WIFI_SSID is required}"
: "${WIFI_PSK:?WIFI_PSK is required}"

RUNTIME=/run/event-wifi
install -d -m 700 "$RUNTIME"
rfkill unblock wifi

mapfile -t rows < <("$ROOT_DIR/.venv/bin/python" - "$ADAPTERS_FILE" <<'PY'
import sys, tomllib
with open(sys.argv[1], "rb") as f:
    for item in tomllib.load(f)["adapter"]:
        print("|".join([item["client_id"], item["interface"], item["namespace"], item.get("mac", "")]))
PY
)

for row in "${rows[@]}"; do
  IFS='|' read -r client iface namespace expected_mac <<< "$row"
  if [[ ! -e "/sys/class/net/$iface" ]]; then
    echo "$client: interface $iface not found" >&2
    exit 1
  fi
  actual_mac=$(cat "/sys/class/net/$iface/address")
  if [[ -n "$expected_mac" && "${actual_mac,,}" != "${expected_mac,,}" ]]; then
    echo "$client: MAC mismatch for $iface ($actual_mac != $expected_mac)" >&2
    exit 1
  fi

  systemctl stop "wpa_supplicant@$iface.service" 2>/dev/null || true
  nmcli device set "$iface" managed no 2>/dev/null || true
  ip link set "$iface" down
  ip netns add "$namespace" 2>/dev/null || true
  ip link set "$iface" netns "$namespace"
  ip netns exec "$namespace" ip link set lo up
  ip netns exec "$namespace" ip link set "$iface" up

  conf="$RUNTIME/$namespace-wpa.conf"
  wpa_passphrase "$WIFI_SSID" "$WIFI_PSK" > "$conf"
  chmod 600 "$conf"
  ip netns exec "$namespace" wpa_supplicant -B \
    -P "$RUNTIME/$namespace-wpa.pid" \
    -i "$iface" -c "$conf"
  ip netns exec "$namespace" dhclient -v \
    -pf "$RUNTIME/$namespace-dhclient.pid" \
    -lf "$RUNTIME/$namespace-dhclient.leases" "$iface"

  echo "$client ready in namespace $namespace"
  ip netns exec "$namespace" iw dev "$iface" link
  ip netns exec "$namespace" ip -brief address show dev "$iface"
done

