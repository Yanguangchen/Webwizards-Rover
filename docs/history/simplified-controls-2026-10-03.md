# Faster, simpler controls — 3 October 2026

The owner restored power, reported that the earlier signal-loss stop worked, and
requested higher speed and removal of irrelevant controls. Optional clarification
was offered; the implemented moderate default is 30%, adjustable from 10% to 50%.

## Deployed changes

The public driving view now contains eight direction buttons, Stop, speed slider,
voltage and connection status. Removed the stock gimbal, GPIO, network and JSON
console UI. The manufacturer's local UI and controller firmware are unchanged.
Kept sequence checks, one-use tokens, 500 ms expiry and 350 ms controller watchdog.
A speed change while held stops movement until a fresh press.

Backed up existing runtime files on the Pi to
`~/rover-public-control/backup-before-simple-ui-20261003-035416/`. Installed the four
current runtime UI/motion files and restarted rover-controls. Service remained
enabled and driving remained enabled.

## Verification

- 12 simulated motion, 7 HTTP relay and 7 browser tests passed.
- Browser preview rendered successfully with no console errors.
- Local authenticated UI, session and T130 telemetry returned HTTP 200.
- Session: enabled=true, ready=true, maxSpeed=0.25, leaseMs=500, watchdogMs=350.
- Battery about 11.8 V. No nonzero motor command was used for verification.
- The user must reload existing controls to receive the new client.

## Separate connection limitation

The tunnel initially had four connections after boot, but later returned HTTP
502/530 with no ready connections. Cellular HTTPS timed out after eight seconds;
Wi-Fi HTTPS to the same target returned 200 in 0.18 seconds. The modem kept its
address/default route, so route preference did not trigger fallback. A tunnel
restart timed out. Cellular preference and controller driving remained enabled.
The underlying cellular internet fault is unresolved.

## Repository publication

Consolidated rover-specific knowledge, scripts, services, tests, models and pitch
assets. Removed private credentials, raw reference photos, screenshot/login data
and model-render absolute-path metadata. The original private files remain local.
