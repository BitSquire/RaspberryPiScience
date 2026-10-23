# WiFi Signal Meter

A touchscreen-friendly gauge for Raspberry Pi OS that shows the signal
strength of the WiFi network you're already connected to.

- 180-degree dial with four bands: **gray** (not connected), **red**
  (barely reachable), **yellow** (fair), **green** (good/strong).
- Reads the current connection's signal via `nmcli` (NetworkManager, the
  default on current Raspberry Pi OS), falling back to `iwconfig` and
  then `/proc/net/wireless` if needed — no extra setup required.
- Updates every 2 seconds. Shows SSID, dBm, and last-update time below
  the dial.

## Installing on the Pi

Copy `wifi-signal-meter.tar.gz` to the Pi (scp, USB drive, etc.), then:

```bash
tar -xzf wifi-signal-meter.tar.gz
cd wifi-signal-meter
./install.sh
```

`install.sh` installs `python3-tk` if it's missing and optionally sets
up an autostart entry for fullscreen kiosk mode. No other packages are
needed — the app only calls out to standard command-line tools
(`nmcli`/`iwconfig`) that already ship with Raspberry Pi OS.

To rebuild the archive after making changes, run `./package.sh` — it
writes a fresh `wifi-signal-meter.tar.gz` next to it.

## Running

```bash
python3 main.py
```

Options:

```bash
python3 main.py --interface wlan0   # WiFi interface name (default: wlan0)
python3 main.py --fullscreen        # kiosk mode for the touchscreen
python3 main.py --size 480          # dial diameter in pixels
```

In fullscreen mode, press `Esc` to leave fullscreen or `q` to quit.

If your WiFi adapter isn't `wlan0`, find its name with:

```bash
nmcli device status
```

## Running full screen on boot (optional)

`install.sh` offers to set this up for you. To do it manually instead:

```bash
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/wifi-meter.desktop <<EOF
[Desktop Entry]
Type=Application
Name=WiFi Signal Meter
Exec=python3 "$(pwd)/main.py" --fullscreen
EOF
```

## Files

- `main.py` — application entry point and polling loop
- `gauge.py` — the Tkinter canvas gauge widget
- `wifi_signal.py` — reads signal strength/SSID from the OS
- `install.sh` — installs dependencies and optional autostart entry
- `package.sh` — builds the `wifi-signal-meter.tar.gz` archive
