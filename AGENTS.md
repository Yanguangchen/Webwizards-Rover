# Working on Webwizards Rover

Read `SKILL.md` and the relevant reference before changing deployment behavior. The README records the latest known state; dated history is evidence, not live status.

Tests must use simulated controllers. Do not point test requests at the real rover. Packaging and documentation work needs no motor movement. Distinguish prepared changes, deployed changes and physical verification.

Preserve the owner's requested driving-enabled and cellular-preferred operation. Restore temporary mode changes within the task and report the outcome. Do not silently remove command expiry, stop handling, speed limits or authentication to debug latency.

Never commit passwords, keyed URLs, connector tokens, private keys, Chromium profiles, private photographs, SD-card personalization or APK signing material.

These sources include the October 3 speed and simplified-interface update. The owner restored power and authorized that deployment. Packaging alone does not require SSH or hardware actions; confirm current task scope and live state before operating the robot.
