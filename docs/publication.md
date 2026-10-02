# Publication manifest

This repository consolidates rover-specific work from the setup, recovery, audio,
cellular, controls, modeling and pitch sessions. It is a public source/artifact
archive, not an SD-card image or full backup of the Pi.

Included:
- The rover skill, updated references and useful operating scripts.
- Current control relay, safety code, network recovery, user/system unit examples and tests.
- Cellular APK/source and Bluetooth reconnection source.
- Sanitized dated knowledge records.
- Both model revisions, GLB exports, construction scripts and product renders.
- The pitch deck, source and four cleaned white-background product photographs.

Excluded deliberately:
- OS/Wi-Fi passwords, control keys, full keyed links and Cloudflare connector tokens.
- Personalized cloud-init files, Chromium profiles, login state and APK signing keys.
- Raw room/photographer images, private webcam screenshots and the personal voice recording.
- Installed Blender/Imager/cloudflared binaries, OS images, third-party source downloads,
  duplicate ZIP bundles, temporary build output, logs and incorrect intermediate models.
- The full separate StampNote application checkout. Its source remains in
  [Yanguangchen/StampNote](https://github.com/Yanguangchen/StampNote).

Blender copies were sanitized by removing packed reference photographs and their
reference objects. Robot geometry remains editable. The construction scripts now
look only in an explicitly provided private-reference-photos directory for optional
references; that directory is ignored by Git.

The September pitch is preserved as a historical artifact. Its description of
then-unfinished remote driving is not a current deployment status. The latest model
is design/v2; v1 is retained only for history. Estimated dimensions are not suitable
for fabrication without measurement.

Documentation mentions private file locations and historic screenshots to explain
the deployment; the actual private files/screenshots are not included.
