# MS-PS1CN speaker and StampNote audio

This deployment uses PulseAudio in rover's user session, not PipeWire.
MS-PS1CN was paired/trusted. The known Bluetooth address and sink are configured
in [audio/rover-speaker-connect](../audio/rover-speaker-connect).

The timer reconnects only this paired speaker, selects A2DP, makes it the default
output and moves active streams there. On a recovered connection/route it restores
75% volume and unmutes. While already connected/selected, polling preserves later
volume/mute adjustments.

Install source paths:
- helper: `~/.local/bin/rover-speaker-connect`;
- units: `~/.config/systemd/user/rover-speaker.service` and `.timer`;
- create `~/.local/state/rover-speaker/` for log output.

```sh
systemctl --user status rover-speaker.timer
pactl get-default-sink
pactl list short sinks
pactl list short sink-inputs
```

If diagnosing from root, run as rover with XDG_RUNTIME_DIR=/run/user/1000.
A speaker can be paired but unavailable because it is off or connected elsewhere.
Do not continuously repair a healthy output or replace the user's later volume choice.

Chromium must include `--autoplay-policy=no-user-gesture-required`.
The current launcher includes that flag, kiosk mode and session-crash suppression.
New flags require restarting the existing browser, preserving its profile.
The robotic-control page remains the exact destination.

When requested, a local test can use:
```sh
paplay /usr/share/sounds/alsa/Front_Center.wav
```
Report its exit status; that does not prove human audibility. Test StampNote Talk
and Voice message separately because local speaker playback does not prove WebRTC,
cloud signaling or autoplay end to end.

The speaker timer was verified by a disconnect/reconnect test; its later cold-boot
behavior was not tested in that same session. See [the original audio record](../audio/README.md).
