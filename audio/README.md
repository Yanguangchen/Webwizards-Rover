# Rover speaker automatic reconnection

Installed on roverpi as user rover (UID 1000), 2026-09-24.

## Diagnosis

The StampNote boot service succeeded before SSH login, and Chromium was running the robotic-control URL with the autoplay and kiosk flags. MS-PS1CN remained paired and trusted but disconnected, so PulseAudio routed audio to the Pi headphone output.

## Installed files

- /home/rover/.local/bin/rover-speaker-connect
- /home/rover/.config/systemd/user/rover-speaker.service
- /home/rover/.config/systemd/user/rover-speaker.timer

The enabled timer runs after the user manager starts and 15 seconds after each completed attempt. User lingering was already enabled, so it starts at boot without SSH. It uses the existing PulseAudio service, reconnects only the known paired speaker, selects A2DP, restores default output and 75% volume when recovering a connection or route, and moves existing streams to the speaker. Normal polling preserves subsequent volume and mute changes while the speaker stays connected and selected.

Speaker: MS-PS1CN, Bluetooth address 41:42:BB:24:7E:A1.
PulseAudio sink: bluez_sink.41_42_BB_24_7E_A1.a2dp_sink.

## Verification

- Unit validation passed; timer enabled and active.
- Deliberately disconnected the speaker once.
- First connection attempt was canceled; the scheduled retry recovered it automatically after about 45.8 seconds.
- All active PulseAudio streams were routed to the Bluetooth speaker.
- Volume 75%, unmuted.
- paplay /usr/share/sounds/alsa/Front_Center.wav exited 0. Physical audibility was not independently observed.
- Service Result=success, ExecMainStatus=0.
- No Pi reboot was performed after installing this audio service.

## Diagnostics

Run as rover:

```sh
systemctl --user status rover-speaker.timer
systemctl --user show rover-speaker.service -p Result -p ExecMainStatus
systemctl --user list-timers rover-speaker.timer
cat ~/.local/state/rover-speaker/events.log
bluetoothctl info 41:42:BB:24:7E:A1
pactl get-default-sink
pactl list short sinks
```

The speaker must be powered on and available for a connection. The timer continues retrying if it is temporarily unavailable.
