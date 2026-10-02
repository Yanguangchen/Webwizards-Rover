# Troubleshooting the rover stream

Diagnose from the bottom up. Do not label a failure as a StampNote crash until the Pi and browser have been proven reachable.

## 1. Pi reachability and unexpected reboot

Try mDNS first:

```bash
ssh -o ConnectTimeout=8 rover@roverpi.local
```

If name resolution fails, inspect the current LAN/ARP table or router leases and locate the Pi again. An old address such as `192.168.1.3` is evidence, not a stable configuration.

Once connected, collect:

```bash
uptime
iw dev wlan0 link
vcgencmd get_throttled
last -x | head -20
journalctl -b -1 -n 100 --no-pager
```

Interpret carefully:

- A very short uptime proves a reboot occurred.
- Strong Wi-Fi after reboot does not prove Wi-Fi was healthy before it.
- `throttled=0x0` describes the current boot and does not rule out a previous power interruption.
- SSH timeout plus an absent mDNS record points below the website layer: power, boot, Wi-Fi association, or network reachability.

## 2. User services and exact page

Check:

```bash
systemctl --user status rover-stream-boot rover-site-display rover-site-browser --no-pager
rover-stream status
curl -s http://127.0.0.1:9222/json/list
```

Recover with:

```bash
rover-stream restart
```

The browser target must be the exact `/robotic-control` URL. The launcher binds Chromium's DevTools endpoint to `127.0.0.1:9222`; do not expose it on the LAN.

For inspection from another machine, use a local tunnel:

```bash
ssh -N -L 127.0.0.1:9223:127.0.0.1:9222 rover@roverpi.local
```

## 3. Chromium profile lock

After an abrupt reboot, `~/.config/chromium/SingletonLock` may remain. The maintained launcher moves only a proven stale lock into `~/.local/state/rover-stream/stale-lock-*`.

Before any manual action, inspect:

```bash
readlink ~/.config/chromium/SingletonLock
pgrep -a chromium
```

Never delete the Chromium profile. Never move the lock if its PID is alive or its ownership cannot be proven.

## 4. Webcam device

Check the kernel device independently of Chromium:

```bash
v4l2-ctl --list-devices
v4l2-ctl -d /dev/video0 --list-formats-ext
fuser /dev/video0
timeout 8 v4l2-ctl -d /dev/video0 --stream-mmap --stream-count=5 --stream-to=/dev/null
```

If the direct capture fails, solve USB power, cable, device-node, permissions, or another process holding the camera before changing browser flags.

If direct capture works but browser device enumeration hangs, retain these known-good launcher choices:

- Xvfb display `:99` at 1280x800x24
- `--disable-gpu`
- `--disable-features=WebRtcPipeWireCamera`
- `--disable-background-timer-throttling`
- `--disable-renderer-backgrounding`
- `--disable-backgrounding-occluded-windows`

This Pi uses X11/Xvfb and has no PipeWire or WirePlumber user service. Disabling the PipeWire camera path restored direct V4L2 enumeration for the C270.

Read Chromium logs with:

```bash
rover-stream logs
```

Useful success evidence includes detection of `/dev/video0`, `display_name: C270 HD WEBCAM`, a successful device launch, `VIDEO_CAPTURE_STATE_STARTED`, and `First frame received`.

## 5. Browser permission and video verification

Camera permission is persisted only for `https://stampnote-omega.vercel.app:443`. Do not grant a broader default.

The strongest browser-side verification is:

```javascript
Array.from(document.querySelectorAll("video")).map((video) => ({
  width: video.videoWidth,
  height: video.videoHeight,
  paused: video.paused,
  time: video.currentTime,
  tracks: video.srcObject?.getVideoTracks().map((track) => ({
    label: track.label,
    state: track.readyState,
  })),
}));
```

Expected values are 1280x720, `paused: false`, increasing `currentTime`, label `C270 HD WEBCAM`, and state `live`.

`enumerateDevices()` can block while the camera backend is unhealthy. Bound diagnostic evaluations with a timeout rather than allowing automation to hang indefinitely.

## 6. StampNote sign-in and Live tunnel

The local webcam preview can run while signed out. Live tunnel publication requires the existing Firebase/Google sign-in.

When the Google popup closes and the viewer briefly becomes white, re-check the original tab. A `Sign out of account` button proves authentication completed. Do not ask the user to disclose their Google password or MFA code.

The current StampNote client sends a heartbeat every 8 seconds and considers a publisher stale after 25 seconds. Therefore:

- a Pi reboot, Wi-Fi gap, suspended browser, failed heartbeat request, or stopped page can make the robot appear offline;
- restarting the camera recreates the publisher;
- the status `Streaming video — Live tunnel can share this camera.` means the prerequisites are present, but remote viewing should still be verified when requested.

If the page is signed in and the camera is live but the robot remains offline, inspect browser console/network errors and the site's Live tunnel publisher rather than repeatedly restarting Linux.

## 7. Local remote-control viewer

A localhost dashboard such as `http://localhost:4848/` depends on all of these local components:

- the Pi's Chromium DevTools port;
- an SSH tunnel to that port;
- the local browser-control session and dashboard.

If this viewer says offline while SSH and StampNote are healthy, restore the SSH tunnel/dashboard. Do not restart the Pi merely to fix the observer connection.

## 8. Black remote picture with a working local camera

On 3 October 2026, Firestore reported exhausted quota while the Pi's C270 was
capturing and the page said Streaming. The owner upgraded the Firebase project
to Blaze; quota errors cleared and changing frames reached the Live tunnel.
Restarting Chromium alone had not fixed that backend problem.

Inspect publisher console/network errors for quota, permission and authentication
failures. Check an administrator's Live tunnel for changing frames; local preview
and the Streaming label do not prove successful remote publication. Do not reset
the signed-in profile or change billing without the owner's instruction.

The deployed fallback sent images roughly every 550 ms and heartbeats every
8 seconds, even without a viewer. These are dated implementation observations,
not current pricing or a guarantee of quota capacity. Source optimizations were
not made in this repository.

For audio autoplay and Bluetooth recovery, see [audio.md](audio.md). Keep
`--autoplay-policy=no-user-gesture-required` on the existing graphical Chromium
session. For controls Host Error, see [controls.md](controls.md); that tunnel
is a separate path from StampNote video publication.
