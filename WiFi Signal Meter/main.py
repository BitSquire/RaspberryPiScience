#!/usr/bin/env python3
"""WiFi Signal Meter - a touchscreen-friendly gauge showing the current
WiFi connection's signal strength, for Raspberry Pi OS.

Run with no arguments for a normal window, or --fullscreen for kiosk mode.
"""

import argparse
import tkinter as tk
from datetime import datetime

from gauge import SignalGauge, BG_COLOR, TEXT_COLOR, DIM_TEXT_COLOR
from wifi_signal import get_wifi_status

POLL_INTERVAL_MS = 2000


class WifiMeterApp:
    def __init__(self, root, interface="wlan0", gauge_size=420, fullscreen=False):
        self.root = root
        self.interface = interface
        self.root.title("WiFi Signal Meter")
        self.root.configure(bg=BG_COLOR)

        if fullscreen:
            self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))
        self.root.bind("<q>", lambda e: self.root.destroy())

        self.gauge = SignalGauge(root, size=gauge_size)
        self.gauge.pack(padx=20, pady=(20, 5))

        self.detail_label = tk.Label(
            root, text="", bg=BG_COLOR, fg=DIM_TEXT_COLOR, font=("DejaVu Sans", 12)
        )
        self.detail_label.pack(pady=(0, 15))

        self._poll()

    def _poll(self):
        status = get_wifi_status(self.interface)
        self._update_display(status)
        self.root.after(POLL_INTERVAL_MS, self._poll)

    def _update_display(self, status):
        self.gauge.set_value(status.signal_percent, connected=status.connected)

        now = datetime.now().strftime("%H:%M:%S")
        if status.connected:
            parts = [status.ssid or "Unknown network"]
            if status.signal_dbm is not None:
                parts.append(f"{status.signal_dbm} dBm")
            parts.append(f"updated {now}")
            self.detail_label.config(text="  |  ".join(parts))
        else:
            self.detail_label.config(text=f"No WiFi connection  |  updated {now}")


def main():
    parser = argparse.ArgumentParser(description="WiFi Signal Meter")
    parser.add_argument("--interface", default="wlan0", help="WiFi interface name (default: wlan0)")
    parser.add_argument("--fullscreen", action="store_true", help="Start in fullscreen kiosk mode")
    parser.add_argument("--size", type=int, default=420, help="Gauge diameter in pixels")
    args = parser.parse_args()

    root = tk.Tk()
    WifiMeterApp(root, interface=args.interface, gauge_size=args.size, fullscreen=args.fullscreen)
    root.mainloop()


if __name__ == "__main__":
    main()
