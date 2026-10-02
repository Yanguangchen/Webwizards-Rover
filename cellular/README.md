# Rover USB Link

Small helper for the user's Android 4.4.4 UFI cellular modem. It enables USB
tethering using the modem's ConnectivityManager API on boot, USB connection,
or an explicit administrator broadcast. It does not modify firmware or require
root on the modem, and has no internet permission or credential access.

The receiver requires the system DUMP permission of its sender, restricting
explicit broadcasts to the system and diagnostic shell. It skips the request
if a USB interface is already tethered. Logs use the tag `RoverUsbLink`.

Build on the Pi with official Debian aapt, smali, apksigner and Java tools.
The resource table is read from this modem's own framework-res.apk. Keep the
signing key private for future updates.

Install and trigger with an authorized local ADB connection:

```sh
adb -s 0 install rover-usb-link.apk
adb -s 0 shell am broadcast --include-stopped-packages \
  -a local.rover.usbtether.ENABLE \
  -n local.rover.usbtether/.EnableReceiver
adb -s 0 logcat -d -s RoverUsbLink:I '*:S'
```

Remove with `adb -s 0 uninstall local.rover.usbtether`. Removal stops future
automatic enabling; it does not disconnect a currently active USB tether.

Version 1.1 also calls the normal network-permission `tether(interface)` API
when a USB interface is available but untethered. This firmware can report
success for `setUsbTethering(true)` while leaving rndis0 unaddressed.

The Pi also runs `rover-cellular-usb.timer`, which checks 20 seconds after boot
and every 30 seconds thereafter. A working addressed USB link is left alone.
Otherwise the script verifies the known UFI USB identity, briefly connects over
localhost-only ADB port 5038 and triggers the helper. It closes that diagnostic
server afterwards. If NetworkManager exhausted DHCP retries, it restarts only
a disconnected/failed USB profile, without touching Wi-Fi or active links.

To stop the Pi retry layer: `sudo systemctl disable --now rover-cellular-usb.timer`.
The APK's boot/USB receiver continues to operate independently while installed.
