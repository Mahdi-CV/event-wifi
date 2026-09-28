#!/usr/bin/env bash
set -euo pipefail

if [[ ${EUID} -eq 0 ]]; then
  echo "Run this script as your normal user; it invokes sudo when needed." >&2
  exit 1
fi

sudo apt-get update
sudo apt-get install -y \
  python3-venv python3-pip iproute2 iw wpasupplicant isc-dhcp-client \
  rfkill usbutils jq curl

python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e '.[dev]'

echo "Bootstrap complete. Copy and edit the example configuration files."

