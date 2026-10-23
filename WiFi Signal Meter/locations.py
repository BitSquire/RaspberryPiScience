"""Persists named locations and the signal level recorded at each one."""

import json
from pathlib import Path

LOCATIONS_FILE = Path(__file__).resolve().parent / "locations.json"


def load_locations():
    try:
        with open(LOCATIONS_FILE) as f:
            data = json.load(f)
        return {str(name): int(level) for name, level in data.items()}
    except (OSError, ValueError):
        return {}


def save_locations(locations):
    with open(LOCATIONS_FILE, "w") as f:
        json.dump(locations, f, indent=2, sort_keys=True)
