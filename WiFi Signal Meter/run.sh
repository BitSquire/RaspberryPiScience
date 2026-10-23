#!/bin/bash
# Launches the WiFi Signal Meter, pulling the latest version from git
# first if this directory is a git checkout (safe to run either way).

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    if ! git pull --ff-only --quiet; then
        echo "Update check failed (offline, or local changes) — continuing with current version." >&2
    fi
fi

exec python3 "$SCRIPT_DIR/main.py" "$@"
