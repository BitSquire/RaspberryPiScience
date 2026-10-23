"""Reads the current WiFi connection's signal strength using whatever
tool is available on the system (nmcli, then iwconfig, then /proc/net/wireless).
"""

import re
import subprocess
from dataclasses import dataclass
from typing import Optional


@dataclass
class WifiStatus:
    connected: bool
    ssid: Optional[str] = None
    signal_percent: Optional[int] = None  # 0-100
    signal_dbm: Optional[int] = None


def _run(cmd):
    try:
        return subprocess.run(
            cmd, capture_output=True, text=True, timeout=2
        ).stdout
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        return None


def _dbm_to_percent(dbm: float) -> int:
    # Typical WiFi usable range is about -90 dBm (unusable) to -30 dBm (excellent).
    percent = (dbm + 90) * (100 / 60)
    return max(0, min(100, round(percent)))


def _via_nmcli() -> Optional[WifiStatus]:
    out = _run(["nmcli", "-t", "-f", "ACTIVE,SSID,SIGNAL", "dev", "wifi"])
    if out is None:
        return None
    for line in out.strip().splitlines():
        parts = line.split(":")
        if len(parts) < 3:
            continue
        active, ssid, signal = parts[0], parts[1], parts[2]
        if active == "yes":
            try:
                percent = int(signal)
            except ValueError:
                percent = None
            return WifiStatus(connected=True, ssid=ssid or None, signal_percent=percent)
    return WifiStatus(connected=False)


def _via_iwconfig(interface: str) -> Optional[WifiStatus]:
    out = _run(["iwconfig", interface])
    if not out:
        return None
    if "Not-Associated" in out or "Access Point: Not-Associated" in out:
        return WifiStatus(connected=False)

    ssid_match = re.search(r'ESSID:"([^"]*)"', out)
    dbm_match = re.search(r"Signal level=(-?\d+)\s*dBm", out)
    quality_match = re.search(r"Link Quality=(\d+)/(\d+)", out)

    if not dbm_match and not quality_match:
        return None

    ssid = ssid_match.group(1) if ssid_match else None
    dbm = int(dbm_match.group(1)) if dbm_match else None
    if dbm is not None:
        percent = _dbm_to_percent(dbm)
    elif quality_match:
        percent = round(int(quality_match.group(1)) / int(quality_match.group(2)) * 100)
    else:
        percent = None

    return WifiStatus(connected=True, ssid=ssid, signal_percent=percent, signal_dbm=dbm)


def _via_proc_wireless(interface: str) -> Optional[WifiStatus]:
    try:
        with open("/proc/net/wireless") as f:
            lines = f.readlines()
    except OSError:
        return None

    for line in lines[2:]:
        fields = line.split()
        if not fields:
            continue
        if fields[0].rstrip(":") != interface:
            continue
        try:
            dbm = float(fields[3])
        except (IndexError, ValueError):
            return None
        percent = _dbm_to_percent(dbm)
        return WifiStatus(connected=True, signal_percent=percent, signal_dbm=round(dbm))

    return WifiStatus(connected=False)


def get_wifi_status(interface: str = "wlan0") -> WifiStatus:
    """Best-effort read of the current WiFi connection's signal strength."""
    for reader in (_via_nmcli, lambda: _via_iwconfig(interface), lambda: _via_proc_wireless(interface)):
        status = reader()
        if status is not None:
            return status
    return WifiStatus(connected=False)


if __name__ == "__main__":
    print(get_wifi_status())
