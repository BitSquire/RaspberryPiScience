# WiFi Signal Meter

A touchscreen-friendly gauge for Raspberry Pi OS that shows the signal
strength of the WiFi network you're already connected to.

- 180-degree dial with four bands: **gray** (not connected), **red**
  (barely reachable), **yellow** (fair), **green** (good/strong).
- Reads the current connection's signal via `nmcli` (NetworkManager, the
  default on current Raspberry Pi OS), falling back to `iwconfig` and
  then `/proc/net/wireless` if needed — no extra setup required.
- Samples every 2 seconds. Shows SSID, dBm, and when that sample was
  taken below the dial, including a live "Ns ago" counter that ticks
  every second between samples.
- Left-hand list always shows the live "Roaming" reading, plus any
  locations you've recorded (tap **Record Location**, name the spot) —
  sorted alphabetically with the level at the time you recorded it.
  Saved to `locations.json` next to the app, so it survives restarts.
- An on-screen `✕` in the top-right corner exits fullscreen (tap again
  to quit) since a kiosk touchscreen has no keyboard.

## Installing on the Pi (with auto-update)

Cloning the repo (rather than copying a tarball) lets the app pull the
latest version from git every time it starts — see "Auto-update on
startup" below. `RaspberryPiScience` is a private repo, so the Pi needs
its own read-only access to it first:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/raspberrypiscience_deploy -N ""
cat >> ~/.ssh/config <<'EOF'

Host github-raspberrypiscience
    HostName github.com
    User git
    IdentityFile ~/.ssh/raspberrypiscience_deploy
    IdentitiesOnly yes
EOF
cat ~/.ssh/raspberrypiscience_deploy.pub
```

Paste the printed public key into GitHub yourself: repo **Settings →
Deploy keys → Add deploy key** (no need to tick "Allow write access").
Then clone the repo using that alias:

```bash
git clone github-raspberrypiscience:BitSquire/RaspberryPiScience.git ~/RaspberryPiScience
cd ~/RaspberryPiScience/"WiFi Signal Meter"
./install.sh
```

`install.sh` installs `python3-tk` if it's missing and optionally sets
up an autostart entry (using `run.sh`, see below) for fullscreen kiosk
mode. No other packages are needed — the app only calls out to standard
command-line tools (`nmcli`/`iwconfig`) that already ship with Raspberry
Pi OS.

### Alternative: plain tarball (no auto-update)

For a quick one-off install without git, copy `wifi-signal-meter.tar.gz`
to the Pi (scp, USB drive, etc.) instead:

```bash
tar -xzf wifi-signal-meter.tar.gz
cd wifi-signal-meter
./install.sh
```

This works the same way, just without the auto-update step in `run.sh`
(there's no `.git` directory to pull from). Rebuild the archive after
making changes with `./package.sh`, which writes a fresh
`wifi-signal-meter.tar.gz` next to it.

## Auto-update on startup

`run.sh` is the normal way to launch the app (and what the autostart
entry uses). Each time it runs, if the app's directory is a git
checkout, it does a `git pull --ff-only` first — picking up anything
pushed to `RaspberryPiScience` since the last run — then starts the
app. If there's no network, or the pull can't fast-forward, it just
logs that and starts with whatever version is already on disk; it
never blocks startup or overwrites local changes.

## Running

```bash
./run.sh
```

Options (passed straight through to `main.py`):

```bash
./run.sh --interface wlan0   # WiFi interface name (default: wlan0)
./run.sh --fullscreen        # kiosk mode for the touchscreen
./run.sh --size 480          # dial diameter in pixels
```

Run `python3 main.py` directly instead if you want to skip the
update check (e.g. while developing).

In fullscreen mode, tap the `✕` in the top-right corner to leave
fullscreen, tap it again to quit (handy since a kiosk touchscreen has
no keyboard). With a keyboard attached, `Esc` leaves fullscreen and `q`
quits directly.

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
Exec=$(pwd)/run.sh --fullscreen
EOF
```

## Files

- `main.py` — application entry point, layout, and polling loop
- `gauge.py` — the Tkinter canvas gauge widget
- `wifi_signal.py` — reads signal strength/SSID from the OS
- `locations.py` — loads/saves recorded locations (`locations.json`)
- `run.sh` — launches the app, pulling updates first if this is a git checkout
- `install.sh` — installs dependencies and optional autostart entry
- `package.sh` — builds the `wifi-signal-meter.tar.gz` archive
