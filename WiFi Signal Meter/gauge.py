"""A 180-degree arc gauge widget drawn on a Tkinter Canvas.

The arc sweeps from 180 (left) to 0 (right) degrees, through 90 (top).
It is divided into four fixed bands, left to right:
  gray   - not connected (reserved zone, needle parks here when offline)
  red    - barely reachable
  yellow - fair
  green  - good / excellent
"""

import math
import tkinter as tk

GRAY = "#888888"
RED = "#d93b3b"
YELLOW = "#e0b400"
GREEN = "#3fae4a"
NEEDLE_COLOR = "#eaeaea"
PIVOT_COLOR = "#eaeaea"
BG_COLOR = "#1c1c1c"
FACE_COLOR = "#151515"
TEXT_COLOR = "#f0f0f0"
DIM_TEXT_COLOR = "#999999"

# Band boundaries as a fraction of the 0-100 gauge scale.
GRAY_END = 8
RED_END = 40
YELLOW_END = 72
GREEN_END = 100

START_ANGLE = 180  # leftmost point of the arc
SWEEP = 180        # degrees covered, sweeping clockwise to 0

# Vertical layout, independent of radius: top margin for the arc,
# then the pivot line, then fixed space below for the readout text.
TOP_MARGIN = 20
LABEL_MARGIN = 26  # extra space reserved for tick labels above the arc
TEXT_AREA_HEIGHT = 100

MARKER_RADIUS = 11


def _value_to_angle(value: float) -> float:
    """Map a 0-100 gauge value to an angle in degrees (180 -> 0)."""
    value = max(0, min(100, value))
    return START_ANGLE - (value / 100) * SWEEP


class SignalGauge(tk.Canvas):
    def __init__(self, parent, size=400, **kwargs):
        self.size = size
        self.radius = size / 2 - 20
        self.cx = size / 2
        self.cy = TOP_MARGIN + LABEL_MARGIN + self.radius
        height = int(self.cy + TEXT_AREA_HEIGHT)

        super().__init__(parent, width=size, height=height, bg=BG_COLOR,
                          highlightthickness=0, **kwargs)

        self._draw_static()
        self._needle = None
        self._pivot = None
        self._value_text = None
        self._status_text = None
        self._markers = []
        self.set_value(0, connected=False)

    def _band_extent(self, start_pct, end_pct):
        start_angle = _value_to_angle(end_pct)
        extent = ((end_pct - start_pct) / 100) * SWEEP
        return start_angle, extent

    def _draw_static(self):
        r = self.radius
        bands = [
            (0, GRAY_END, GRAY),
            (GRAY_END, RED_END, RED),
            (RED_END, YELLOW_END, YELLOW),
            (YELLOW_END, GREEN_END, GREEN),
        ]
        thickness = r * 0.32
        outer = r
        inner = r - thickness

        for start_pct, end_pct, color in bands:
            start_angle, extent = self._band_extent(start_pct, end_pct)
            self.create_arc(
                self.cx - outer, self.cy - outer, self.cx + outer, self.cy + outer,
                start=start_angle, extent=extent,
                fill=color, outline=BG_COLOR, width=2, style=tk.PIESLICE,
            )
        # punch out the center to turn pie slices into a ring
        self.create_oval(
            self.cx - inner, self.cy - inner, self.cx + inner, self.cy + inner,
            fill=FACE_COLOR, outline=BG_COLOR, width=2,
        )

        # tick labels at band boundaries
        for pct, label in ((GRAY_END, ""), (RED_END, "weak"),
                           (YELLOW_END, "fair"), (GREEN_END, "strong")):
            angle = math.radians(_value_to_angle(pct))
            lx = self.cx + (outer + 16) * math.cos(angle)
            ly = self.cy - (outer + 16) * math.sin(angle)
            if label:
                anchor = "w" if pct >= GREEN_END else ("e" if pct <= RED_END else "center")
                self.create_text(lx, ly, text=label, fill=DIM_TEXT_COLOR,
                                  font=("DejaVu Sans", 10), anchor=anchor)

        # pivot cap
        self.create_oval(
            self.cx - 10, self.cy - 10, self.cx + 10, self.cy + 10,
            fill=PIVOT_COLOR, outline=PIVOT_COLOR,
        )

    def set_value(self, percent, connected=True, caption=None):
        """Move the needle. When connected is False, it parks in the gray band."""
        display_value = _display_value(percent, connected)
        angle = math.radians(_value_to_angle(display_value))
        length = self.radius - (self.radius * 0.32) / 2

        x = self.cx + length * math.cos(angle)
        y = self.cy - length * math.sin(angle)

        if self._needle is not None:
            self.delete(self._needle)
        if self._pivot is not None:
            self.delete(self._pivot)
        needle_color = NEEDLE_COLOR if connected else GRAY
        self._needle = self.create_line(
            self.cx, self.cy, x, y, fill=needle_color, width=5, capstyle=tk.ROUND
        )
        self._pivot = self.create_oval(
            self.cx - 9, self.cy - 9, self.cx + 9, self.cy + 9,
            fill=PIVOT_COLOR, outline=PIVOT_COLOR,
        )

        if self._value_text is not None:
            self.delete(self._value_text)
        if self._status_text is not None:
            self.delete(self._status_text)

        text_y = self.cy + 36
        main_text = f"{percent}%" if connected and percent is not None else "--"
        self._value_text = self.create_text(
            self.cx, text_y,
            text=main_text, fill=TEXT_COLOR, font=("DejaVu Sans", 30, "bold"),
        )
        status = caption if caption else ("Connected" if connected else "Not Connected")
        status_color = TEXT_COLOR if connected else GRAY
        self._status_text = self.create_text(
            self.cx, text_y + 34,
            text=status, fill=status_color, font=("DejaVu Sans", 14),
        )

    def set_markers(self, markers):
        """Draw small numbered circles on the ring for recorded locations.

        markers: iterable of (number, percent) pairs.
        """
        for item in self._markers:
            self.delete(item)
        self._markers = []

        thickness = self.radius * 0.32
        ring_mid = self.radius - thickness / 2

        for number, percent in markers:
            display_value = _display_value(percent, True)
            angle = math.radians(_value_to_angle(display_value))
            mx = self.cx + ring_mid * math.cos(angle)
            my = self.cy - ring_mid * math.sin(angle)

            circle = self.create_oval(
                mx - MARKER_RADIUS, my - MARKER_RADIUS,
                mx + MARKER_RADIUS, my + MARKER_RADIUS,
                fill=FACE_COLOR, outline=TEXT_COLOR, width=1.5,
            )
            label = self.create_text(
                mx, my, text=str(number), fill=TEXT_COLOR,
                font=("DejaVu Sans", 9, "bold"),
            )
            self._markers.extend([circle, label])

        # keep the live needle/pivot visible above any marker it crosses
        if self._needle is not None:
            self.tag_raise(self._needle)
        if self._pivot is not None:
            self.tag_raise(self._pivot)


def _display_value(percent, connected):
    if not connected or percent is None:
        return GRAY_END / 2  # park needle in the middle of the gray band
    # map 0-100 signal percent onto the red/yellow/green span (skip the gray reserve)
    span = GREEN_END - GRAY_END
    return GRAY_END + (percent / 100) * span
