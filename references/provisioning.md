# Provisioning and boot automation

Use this reference for a new SD card, a reimage, initial configuration, or installing the rover launcher and boot unit.

## Image the SD card

Use the current official Raspberry Pi Imager and Raspberry Pi OS Lite 64-bit for a Raspberry Pi 4.

Before erasing anything:

1. List disks before and after inserting the card.
2. Resolve the exact removable device using device name, removability, partition layout, and reader identity. Capacity alone is not enough.
3. Unmount its volumes.
4. Present the exact target to the user immediately before the destructive write if that write has not already been specifically authorized.

Preconfigure:

- Hostname: `roverpi`
- Username: `rover`
- Wi-Fi SSID and password: obtain privately; do not save them in the skill
- Wireless country: `SG`
- Timezone: `Asia/Singapore`
- SSH: enabled with password authentication for initial access

Choose a strong unique OS password and avoid echoing it. After the first successful connection, prefer an SSH key and retain a recovery path.

If a reimage changes the SSH host key, compare the new fingerprint with a trusted local/console observation before replacing a known-host entry.

## Initial Pi preparation

Install the runtime packages:

```bash
sudo apt update
sudo apt install -y chromium xvfb v4l-utils curl python3
sudo usermod -aG video rover
```

A new `video` group membership takes effect after a new login or reboot.

Inspect the webcam before browser work:

```bash
v4l2-ctl --list-devices
v4l2-ctl -d /dev/video0 --list-formats-ext
timeout 8 v4l2-ctl -d /dev/video0 --stream-mmap --stream-count=5 --stream-to=/dev/null
```

The known C270 exposes MJPEG at 1280x720 and works well at 30 fps. Discover rather than assume `/dev/video0` on a fresh installation.

## Install the launcher

From this skill directory, copy `scripts/rover-stream` and `assets/rover-stream-boot.service` to the Pi, then run `scripts/install-rover-stream.sh` on the Pi from the copied skill directory. The installer:

- installs `rover-stream` in `/usr/local/bin`;
- installs the user boot unit;
- enables linger so the user's systemd manager starts at boot;
- enables and starts the boot unit.

Equivalent commands are:

```bash
sudo install -m755 scripts/rover-stream /usr/local/bin/rover-stream
mkdir -p ~/.config/systemd/user
install -m644 assets/rover-stream-boot.service ~/.config/systemd/user/rover-stream-boot.service
sudo loginctl enable-linger rover
systemctl --user daemon-reload
systemctl --user enable --now rover-stream-boot.service
```

The boot unit waits for the exact robotic-control URL to be reachable. If Wi-Fi is late, systemd retries every 15 seconds.

## Verify boot behavior

Before rebooting, check:

```bash
systemd-analyze --user verify ~/.config/systemd/user/rover-stream-boot.service
systemctl --user status rover-stream-boot rover-site-display rover-site-browser --no-pager
loginctl show-user rover -p Linger
```

After a reboot, reconnect and verify:

```bash
systemctl --user show rover-stream-boot -p ActiveState -p Result -p ActiveEnterTimestamp
systemctl --user is-active rover-site-display rover-site-browser
curl -s http://127.0.0.1:9222/json/list
```

The page target must be `https://stampnote-omega.vercel.app/robotic-control`. If the camera button still says `Start camera`, boot automation is working and page-level automatic activation remains to be implemented.
