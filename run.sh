#!/bin/sh
# Gravy: dashboard + one screening cycle (или цикл по INTERVAL сек)
set -e
cd "$(dirname "$0")"
python3 -m agent.dashboard &
DASH=$!
trap 'kill $DASH 2>/dev/null' EXIT
if [ -n "$1" ] && [ "$1" = "loop" ]; then
  INTERVAL="${GRAVY_INTERVAL:-1800}"
  while true; do
    python3 -m agent.loop || true
    sleep "$INTERVAL"
  done
else
  python3 -m agent.loop
fi
