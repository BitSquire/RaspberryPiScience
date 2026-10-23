#!/bin/bash
# Builds wifi-signal-meter.tar.gz for copying onto the Raspberry Pi.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STAGE_NAME="wifi-signal-meter"
OUT_FILE="$SCRIPT_DIR/${STAGE_NAME}.tar.gz"
STAGE_DIR="$(mktemp -d)/$STAGE_NAME"

mkdir -p "$STAGE_DIR"
cp "$SCRIPT_DIR"/main.py "$SCRIPT_DIR"/gauge.py "$SCRIPT_DIR"/wifi_signal.py \
   "$SCRIPT_DIR"/install.sh "$SCRIPT_DIR"/README.md "$STAGE_DIR/"

tar -czf "$OUT_FILE" -C "$(dirname "$STAGE_DIR")" "$STAGE_NAME"
rm -rf "$(dirname "$STAGE_DIR")"

echo "Built $OUT_FILE"
