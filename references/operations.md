# Operating the deployed rover

## Connect and check

Use `ssh rover@roverpi.local`. The last verified home LAN address was192.168.1.1;
that is a historical observation, not a static reservation. If mDNS fails, inspect
the current LAN/ARP table. Preserve the rover's trusted host key when specifying a
discovered address. A Mac on a phone hotspot cannot reach the home LAN SSH address.
The public controls tunnel does not provide SSH.

The user is `rover`, UID1000. User services need that user's systemd/audio session.
Do not run Chromium as root. Useful checks:

```sh
uptime
vcgencmd measure_temp
vcgencmd get_throttled
lsusb -t
ip -4 route get 1.1.1.1
systemctl --user is-active rover-stream-boot rover-site-display rover-site-browser
systemctl --user is-active rover-controls rover-controls-named-tunnel
rover-stream status
```

## Service map

| Unit | Manager | Purpose |
|---|---|---|
| rover-stream-boot.service | user | Opens exact StampNote robotic-control after network is reachable |
| rover-site-display.service | user/transient | Xvfb display99 |
| rover-site-browser.service | user/transient | Chromium; created by rover-stream |
| rover-speaker.timer/service | user | Reconnects paired speaker and restores PulseAudio routing |
| rover-controls.service | user | Loopback8877 authenticated relay and local motion watchdog |
| rover-controls-named-tunnel.service | user | Persistent Cloudflare hostname |
| rover-controls-network-check.timer/service | user | Detects route/interface changes and reconnects tunnel |
| rover-controller-wifi.service | system/root | Creates virtual roverctl interface for controller AP |
| rover-cellular-usb.timer/service | system/root | Restores modem USB tethering and disconnected DHCP |

The user's systemd manager has linger enabled. The old
`rover-controls-tunnel.service` was a Quick Tunnel and is disabled.

## Recovery boundaries

- Browser: `rover-stream restart` preserves the existing profile and sign-in.
- Controls: inspect local controller, relay, tunnel readiness and public HTTP before restarting.
- Speaker: inspect the user's PulseAudio sink before restarting Chromium.
- Cellular: check whether usb0 and the USB modem exist before changing APN or routes.
- Camera: check Linux USB/V4L2 before blaming StampNote.
- Do not reboot to repair only a disconnected local observer/dashboard.
- Back up deployment files before replacing them; report whether new boot behavior was actually tested.

## Logs

```sh
rover-stream logs
systemctl --user show rover-controls -p ActiveState -p SubState -p ExecMainStatus
sudo journalctl _SYSTEMD_USER_UNIT=rover-controls-named-tunnel.service --since '-10 min'
sudo journalctl -u rover-cellular-usb.service --since '-10 min'
sudo journalctl -k --since '-10 min'
```

On this installation, `journalctl --user` sometimes returned no journals.
The system journal filter `_SYSTEMD_USER_UNIT` retrieved the user-unit logs.
Avoid printing full URLs, command payloads, browser tokens or credentials.

## Optional password helpers

`scripts/rover-ssh.exp` and `rover-scp.exp` accept a private password file through
`ROVER_PASSWORD_FILE`. Keep it outside Git with0600 permissions. Prefer ordinary
SSH key authentication when available. These helpers preserve StrictHostKeyChecking;
they do not bootstrap trust. Never put a password in a command argument.
