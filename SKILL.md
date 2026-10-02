---
name: raspberry-pi-rover
description: Operate, configure or troubleshoot this Raspberry Pi rover, including StampNote camera and audio, cellular connectivity, the public controls tunnel and motion safety. Use for roverpi or Webwizards Rover work.
---

# Raspberry Pi Rover

Read the repository README for the last verified deployment and unresolved issues. Treat old addresses and successful tests as historical evidence, not current status.

## Essential facts

- Raspberry Pi4, Raspberry Pi OS Lite64-bit, runtime user `rover`.
- Host `roverpi.local`; discover the current address and preserve SSH host verification.
- Timezone `Asia/Singapore`; wireless country `SG`.
- Camera publisher is **exactly** `https://stampnote-omega.vercel.app/robotic-control`. Never substitute the homepage.
- Headless Chromium runs under Xvfb `:99`; debugging stays on127.0.0.1:9222.
- Preserve `/home/rover/.config/chromium`: it contains sign-in and site permissions.
- Normal browser recovery: `rover-stream restart`, as `rover`, without sudo.
- Controls: `https://rover.webwizardsg.com`, through a named Cloudflare tunnel. Its key and connector token are external to this repository.
- Camera and controls are separate paths. Verify each independently.
- The owner wants cellular preferred and driving enabled. Do not leave driving disabled as an undocumented troubleshooting side effect.

## Choose the relevant instructions

- New SD card, dependencies or camera boot setup: [provisioning](references/provisioning.md).
- Routine startup and service verification: [operations](references/operations.md).
- Camera, sign-in, quota errors or black Live tunnel: [troubleshooting](references/troubleshooting.md).
- SIM/modem, USB disconnects, routes or controller AP: [networking](references/networking.md).
- Public URL, HTTP530/502, delayed presses or excess motion: [controls](references/controls.md).
- Speaker reconnection or autoplay: [audio](references/audio.md).
- Photos, deck and models: [publication manifest](docs/publication.md), then the artifact README.

## Diagnose from the failed layer

1. Establish power and reachability. Check uptime, USB devices, temperature and routes. A modem missing from USB is below the web-app layer.
2. Check user services and the exact Chromium page; do not repeatedly restart Linux.
3. Verify camera frames and existing authentication separately.
4. Verify changing remote frames or authenticated controller responses. A "Streaming" label or running tunnel process alone is insufficient.
5. Make the narrow change, then verify that layer. Stop repeating a failed recovery when new evidence is needed.

## Operational constraints

- Match existing user authorization and current scope. This skill does not authorize billing changes, reimaging, reboots, motor movement or credential publication.
- No nonzero motor tests during camera/network work. Distinguish fake-controller tests from a user-supervised physical stopping test.
- Preserve Chromium's profile and SSH trust. Recover only a proven stale profile lock.
- Run Chromium as the normal user. Preserve autoplay, kiosk, camera-backend and background-timer flags in `scripts/rover-stream`.
- Back up existing files before deployment. Avoid duplicate browser autostarts and the obsolete Quick Tunnel.
- Keep CDP, relay port8877, ADB and metrics ports private.
- Keep passwords, keyed URLs, tokens, browser profiles, SIM identifiers, private source photographs and signing keys out of commits/logs.
- Report sign-in or user actions that remain necessary; local preview does not prove remote publication.

## Completion criteria

Camera recovery requires reachable Pi, active browser/display, exact URL, signed-in state, live capture and changing remote frames. When diagnosing lag, distinguish JPEG fallback from WebRTC video.

Controls recovery requires separate checks of local controller, authenticated relay, tunnel readiness and external HTTPS. Run fake-controller tests for motion changes. Report driving mode, speed limit and whether physical stopping was actually tested.

For boot work, distinguish enabled services from a tested cold boot; reboot only when authorized. Report unresolved modem, battery, power and cooling issues instead of promising always-online operation.
