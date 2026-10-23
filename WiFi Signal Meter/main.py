#!/usr/bin/env python3
"""WiFi Signal Meter - a touchscreen-friendly gauge showing the current
WiFi connection's signal strength, for Raspberry Pi OS.

Run with no arguments for a normal window, or --fullscreen for kiosk mode.
"""

import argparse
import time
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, simpledialog

from gauge import SignalGauge, BG_COLOR, FACE_COLOR, TEXT_COLOR, DIM_TEXT_COLOR, GREEN
from locations import load_locations, save_locations
from wifi_signal import get_wifi_status

POLL_INTERVAL_MS = 2000
TICK_INTERVAL_MS = 1000
EXIT_BUTTON_SIZE = 40
SIDEBAR_WIDTH = 190


class WifiMeterApp:
    def __init__(self, root, interface="wlan0", gauge_size=420, fullscreen=False):
        self.root = root
        self.interface = interface
        self.locations = load_locations()
        self.last_status = None
        self.last_sample_wall = None
        self.last_sample_monotonic = None
        self.root.title("WiFi Signal Meter")
        self.root.configure(bg=BG_COLOR)

        if fullscreen:
            self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))
        self.root.bind("<q>", lambda e: self.root.destroy())

        self._build_sidebar(root)
        self._build_main_area(root, gauge_size)

        # Touch-accessible exit control: there's no keyboard on a kiosk
        # touchscreen, so Escape/q alone leave no way out of fullscreen.
        self.exit_button = tk.Label(
            root, text="✕", bg=BG_COLOR, fg=DIM_TEXT_COLOR,
            font=("DejaVu Sans", 16),
        )
        self.exit_button.place(
            relx=1.0, x=-2, y=2, anchor="ne",
            width=EXIT_BUTTON_SIZE, height=EXIT_BUTTON_SIZE,
        )
        self.exit_button.bind("<Button-1>", self._on_exit_tap)

        self._poll()
        self._tick()

    def _build_sidebar(self, root):
        sidebar = tk.Frame(root, bg=BG_COLOR, width=SIDEBAR_WIDTH)
        sidebar.pack(side="left", fill="y", padx=(12, 6), pady=12)
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar, text="Locations", bg=BG_COLOR, fg=TEXT_COLOR,
            font=("DejaVu Sans", 13, "bold"), anchor="w",
        ).pack(fill="x", pady=(0, 6))

        list_frame = tk.Frame(sidebar, bg=BG_COLOR)
        list_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.listbox = tk.Listbox(
            list_frame, bg=FACE_COLOR, fg=TEXT_COLOR, selectbackground=FACE_COLOR,
            selectforeground=TEXT_COLOR, highlightthickness=0, bd=0,
            font=("DejaVu Sans", 11), activestyle="none",
            yscrollcommand=scrollbar.set,
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)

        tk.Button(
            sidebar, text="Record Location", command=self._on_record_clicked,
            bg=GREEN, fg="white", activebackground=GREEN, activeforeground="white",
            relief="flat", font=("DejaVu Sans", 11), pady=8,
        ).pack(fill="x", pady=(8, 0))

    def _build_main_area(self, root, gauge_size):
        main_area = tk.Frame(root, bg=BG_COLOR)
        main_area.pack(side="left", fill="both", expand=True)

        self.gauge = SignalGauge(main_area, size=gauge_size)
        self.gauge.pack(padx=20, pady=(20, 5))

        self.detail_label = tk.Label(
            main_area, text="", bg=BG_COLOR, fg=DIM_TEXT_COLOR, font=("DejaVu Sans", 12)
        )
        self.detail_label.pack(pady=(0, 15))

    def _on_exit_tap(self, event):
        if self.root.attributes("-fullscreen"):
            self.root.attributes("-fullscreen", False)
        else:
            self.root.destroy()

    def _on_record_clicked(self):
        status = self.last_status
        if status is None or not status.connected or status.signal_percent is None:
            messagebox.showinfo(
                "Not connected", "Can't record a location while not connected to WiFi.",
                parent=self.root,
            )
            return

        name = simpledialog.askstring(
            "Record Location", "Location name:", parent=self.root,
        )
        if name is None:
            return
        name = name.strip()
        if not name:
            return

        self.locations[name] = status.signal_percent
        save_locations(self.locations)
        self._refresh_list(status)

    def _poll(self):
        status = get_wifi_status(self.interface)
        self.last_status = status
        self.last_sample_wall = datetime.now()
        self.last_sample_monotonic = time.monotonic()
        self._update_display(status)
        self.root.after(POLL_INTERVAL_MS, self._poll)

    def _tick(self):
        if self.last_status is not None:
            self._update_detail_label(self.last_status)
        self.root.after(TICK_INTERVAL_MS, self._tick)

    def _update_display(self, status):
        self.gauge.set_value(status.signal_percent, connected=status.connected)
        self._refresh_list(status)
        self._update_detail_label(status)

    def _update_detail_label(self, status):
        elapsed = int(time.monotonic() - self.last_sample_monotonic)
        age = f"{elapsed}s ago" if elapsed != 1 else "1s ago"
        when = f"sampled {self.last_sample_wall.strftime('%H:%M:%S')} ({age})"

        if status.connected:
            parts = [status.ssid or "Unknown network"]
            if status.signal_dbm is not None:
                parts.append(f"{status.signal_dbm} dBm")
            parts.append(when)
            self.detail_label.config(text="  |  ".join(parts))
        else:
            self.detail_label.config(text=f"No WiFi connection  |  {when}")

    def _refresh_list(self, status):
        self.listbox.delete(0, tk.END)

        if status.connected and status.signal_percent is not None:
            roaming_text = f"Roaming — {status.signal_percent}%"
        else:
            roaming_text = "Roaming — --"
        self.listbox.insert(tk.END, roaming_text)
        self.listbox.itemconfig(0, fg=GREEN)

        for name in sorted(self.locations, key=str.lower):
            level = self.locations[name]
            self.listbox.insert(tk.END, f"{name} — {level}%")


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
