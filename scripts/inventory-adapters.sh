#!/usr/bin/env bash
set -euo pipefail

echo -e "INTERFACE\tMAC\tDRIVER\tUSB"
for iface_path in /sys/class/net/*; do
  iface=$(basename "$iface_path")
  [[ -d "$iface_path/wireless" ]] || continue
  mac=$(cat "$iface_path/address")
  driver=$(basename "$(readlink -f "$iface_path/device/driver" 2>/dev/null || echo unknown)")
  device=$(readlink -f "$iface_path/device" 2>/dev/null || echo unknown)
  printf '%s\t%s\t%s\t%s\n' "$iface" "$mac" "$driver" "$device"
done

echo
iw dev

