# Dependencies and attribution

This archive does not assign a new license to third-party material or product marks.

- Robot chassis and revised wheel geometry: [Waveshare WAVE ROVER](https://www.waveshare.com/wiki/WAVE_ROVER).
  The v2 tire/hub geometry was derived from the manufacturer's
  [published model archive](https://files.waveshare.com/upload/e/ec/WAVE_ROVER_MODEL_STL.rar).
  Preserve the attribution and consult the owner's applicable rights before redistribution in other products.
- Webcam dimensional/design reference: [Logitech C270](https://www.logitech.com/en-us/shop/p/c270-hd-webcam)
  and [setup guide](https://secure.logitech.com/assets/46735/4/hd-webcam-c270.pdf).
- Blender4.5 LTS was used to construct/render models. Its application binary is not included.
- Raspberry Pi OS, Chromium, Xvfb, BlueZ, PulseAudio, NetworkManager and systemd
  are runtime dependencies obtained from their official distributions.
- cloudflared is obtained from [Cloudflare](https://github.com/cloudflare/cloudflared).
  The last deployed binary was2026.9.3; the binary and private connector token are not included.
- The modem helper uses Android APIs and requires aapt, smali, keytool and apksigner
  to build. Its included APK contains a public signing certificate, not a signing key.
- The deck source used the Codex presentation runtime's `@oai/artifact-tool`;
  the dependency is not bundled and may require that runtime.
- The separate web application is [StampNote](https://github.com/Yanguangchen/StampNote).
  The remote-controller URL integration was merged through [PR33](https://github.com/Yanguangchen/StampNote/pull/33).

Original prototype photographs belong to the owner. Public product edits use
AI-assisted background cleanup and are not engineering measurements.
