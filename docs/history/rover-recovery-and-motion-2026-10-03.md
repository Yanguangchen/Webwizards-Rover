> Historical diagnostic record. Later entries and the root README take precedence. Credentials and account emails are omitted. Local screenshot paths mentioned below are not published.

# Rover recovery and motion safety — 3 October 2026

## Latest verified state, 03:24 SGT

- **Driving is enabled**, per the user's explicit instruction not to disable it.
- `rover-controls.service` runs `relay.py ... --enable-drive`.
- Public `https://rover.webwizardsg.com/` returned HTTP 200 in 0.256 s.
- Authenticated `/motion/session` returned HTTP 200 in 0.259 s, enabled=true,
  ready=true, maxSpeed=0.15, watchdogMs=350, leaseMs=500. No session/key printed.
- Cloudflare named tunnel readyConnections=4; relay, named tunnel and network
  check timer all active. No recent warning-level relay journal entries.
- StampNote Live tunnel iframe visibly loads the controls and status
  "Stopped — hold a direction to drive. Speed limited to 30%."
- Actual wheel movement and physical stopping distance were **not tested**.
  Read-only T130 at 03:23:53 reports L=0, R=0.
- Final route: home Wi-Fi wlan0, gateway 192.168.1.254. Cellular is still configured
  as preferred when its USB link returns; modem USB disappearance is unresolved.
- Pi temperature fell from 84.7°C (02:52) to 64.7°C; final throttling flags 0xe0000
  are historical, no current low bits. Earlier 0xe0008 was observed.
- Controller battery telemetry fell from about 11.3 V earlier to 10.47 V at03:18,
  9.08 V in the UI and 8.397 V at03:23. User advised to recharge/check power.
  No physical voltage measurement; no proven link to modem resets.

## Firebase / live feed

- User upgraded quota; Firebase console confirmed **Blaze** for stampnote-eedcd.
- Restarted only StampNote via `rover-stream restart` around02:45, preserving profile.
- Pi logged quota errors through02:48:23 despite plan upgrade. They later cleared
  sufficiently for publishing: remote 400x225 JPEG frames visibly appeared and
  frame hashes changed between02:49:57 and02:50:29.
- At final browser inspection videoWidth was1280 and fallback image width400.
  Did not measure final WebRTC frame rate or end-to-end camera delay.
- Screenshots: rover-live-restored-2026-10-03.jpg and
  rover-controls-safety-enabled-2026-10-03.jpg in this work directory.
- No billing settings or payments were changed by the agent.

## Intermittent public controls outage

- Caught public HTTP530 with X-Frame-Options:SAMEORIGIN at02:53:21 while local
  relay was HTTP200 (2.6 ms) and local controller HTTP200 (0.4 s).
- This explains why the browser shows "refused to connect" inside StampNote
  during a Cloudflare tunnel outage; it is not a permanent iframe permission issue.
- USB modem repeatedly disconnected/re-enumerated as05c6:9024/9091. Camera and
  modem are on the shared Genesys hub. User did not clearly confirm whether
  physically untouched; their answer was "just laggy in general."
- Existing network recovery restarted cloudflared on default-route changes, but
  cloudflared spent up to30 s gracefully shutting down before reconnecting.
- Installed improvements: grace-period2s, systemd TimeoutStopSec5, network
  check every5 s (was15), include Linux interface ifindex in route identity so
  rapid USB disconnect/reconnect with identical IP is detected.
- This reduces recovery delay but cannot prevent hardware/network outages.

## Driving issue and deployed changes

User reported a very short forward tap producing excessive travel. Stock UI:
- speed_rate=1, forward L=R=0.5 (full WAVE ROVER PWM).
- separate unsequenced asynchronous GETs for press/release.
- heartbeat repeats last speed every1500 ms.
- only local button mouseup/touchend release handlers; missing cancellation/focus loss.

Local files and deployed equivalents in /home/rover/rover-public-control:
- motion.py: short server-issued tokens, monotonic per-session sequence numbers,
  tokens expire500 ms after issue rather than delayed packet arrival; local worker
  alone sends wheel commands, stops at lease expiry. Controller runtime watchdog
  T136 cmd350 applied when worker connects. Lost controller response clears intent.
- motion-client.js: pointer capture, release/cancel/leave/lostcapture/window blur/
  hidden/pagehide handling; sequenced prepare/drive/stop; no renewal after release;
  replaces stock heartbeat and motion handlers; keyboard holds supported.
- relay.py: authenticated POST motion API; raw wheel T1/T11/T13 and watchdog T136
  passthrough blocked (zero-speed T1 remains a global stop); existing telemetry,
  other original controller UI, key authentication and CSP preserved.
- Default page speed20%; server cap30% (absolute L/R<=0.15). FAST cannot bypass cap.
- Mode defaults disabled in code for safe startup unless --enable-drive; installed
  production unit explicitly enables driving and this was verified.

Temporary remote pause: initially could not reach SSH because Mac was on phone
hotspot172.20.10.x. User agreed to reconnectHOME_WIFI_SSID. Then stopped relay and issued
T1 L=R=0 (response null). Relay is now restored with new protections enabled.
No nonzero motor command was sent by the agent. User never answered the separate
wheels-raised question; do not claim a physical movement/stop test occurred.

Validation: 11 MotionGuard tests +7 HTTP fake-controller tests +4 JS fake-browser
tests passed. Includes stop-before-prepare, stop-before-delayed-drive, lost release,
expired/replayed tokens, speed limits, controller loss, late browser callbacks,
pointer cancel/blur and authentication. JS/Python syntax and systemd units checked.
Tests use simulated controllers only; no robot movement during tests.

Before install, existing relay, route checker and three systemd files backed up
under /home/rover/.config/rover-controls/before-motion-safety-20261003-<timestamp>/.
Staging directory: /home/rover/rover-public-control/staged-safety-20261003/.
No Pi reboot, firmware flash, boot mission change, DNS change, or billing change.

Official command reference: https://www.waveshare.com/wiki/08_Sub-controller_JSON_Command_Set
Official thermal/power reference: https://www.raspberrypi.com/documentation/computers/raspberry-pi.html
