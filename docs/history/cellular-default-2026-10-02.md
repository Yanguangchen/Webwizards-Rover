> Historical diagnostic record. Later entries and the root README take precedence. Credentials and account emails are omitted. Local screenshot paths mentioned below are not published.

# Rover cellular priority — 2 October 2026

User requested cellular/GSM as the default connection.

## Current outcome (later checks supersede the early failures below)

At 15:07 SGT, cellular internet is working on the Pi via usb0 with BOTH modem
and C270 webcam on the user's single expansion hub. Normal and SIM-forced HTTPS
both returned 200 from StampNote, source 192.168.42.133. The exact robotic-control
page has live 1280x720 video with increasing frame time and sharing status.
Android helper version 1.1 plus an enabled Pi recovery timer restore sharing.
Operation is verified with diagnostic connections closed. The final configuration
has not been tested through a full Pi reboot. Remote wheel control is not configured.

## Applied

- Cellular modem appears as USB RNDIS Ethernet `usb0` (USB ID `05c6:9024`, Android/Qualcomm).
- NetworkManager profile `netplan-eth0`, UUID `75a1216a-9d1a-30cd-8aca-ace5526ec021`: autoconnect enabled, IPv4/IPv6 route metric 50, DNS priority 50.
- Wi-Fi profile `netplan-wlan0-HOME_WIFI_SSID`, UUID `e80cab69-2d20-3461-94cc-9b9247700457`: autoconnect enabled, route metric 600, DNS priority 600. Existing IPv6 ignore setting preserved.
- Changes persisted by NetworkManager in `/etc/netplan/90-NM-<UUID>.yaml`.
- Original YAML and generated connection files backed up on the Pi under `/var/backups/rover-cellular/20261002-130406/` before modifications.
- Ran `netplan generate`, `nmcli connection reload`, and `nmcli device reapply` for usb0 and wlan0. No reboot or interface disconnect requested.

## Verified

- Generated NetworkManager profiles retain the chosen metrics and DNS priorities.
- Active default route: modem gateway `192.168.42.129`, device usb0, metric 50.
- Secondary default route: Wi-Fi gateway `192.168.1.254`, device wlan0, metric 600.
- `ip -4 route get 1.1.1.1` selects usb0.
- Fresh SSH over local Wi-Fi still works.
- HTTPS to StampNote robotic-control, with DNS bypassed using curl --resolve: usb0 times out (curl exit 28); wlan0 returns HTTP 200.
- Netplan generation succeeded with a pre-existing permissions warning for `/lib/netplan/00-network-manager-all.yaml`; this unrelated vendor file was not changed.

## Remaining

Cellular internet does NOT yet work. The modem's local USB link and gateway work, but upstream HTTPS times out. Need modem model and SIM provider/APN to investigate SIM activation, data service, signal and modem configuration. Modem currently exposes no ttyUSB/ttyACM/cdc-wdm devices; do not assume ModemManager control.

Wi-Fi remains available when the modem's route disappears. Route metrics alone do not detect or recover from a modem with a working USB link but failed upstream internet. No internet-health failover watchdog was installed. Boot persistence was verified from generated configuration, without a reboot test.

Current Pi addresses are observations, not fixed addresses: usb0 192.168.42.133 and wlan0 192.168.1.1. Continue using roverpi.local for local SSH.

## Later update: Circles.Life APN saved

- User confirmed Circles.Life Singapore SIM; mobile data works when this SIM is in a phone.
- Product supplied: https://shopee.sg/4G-LTE-USB-Modem-Network-Adapter-With-WiFi-Hotspot-SIM-Card-4G-Wireless-Mini-Wifi-Router-Universal-Network-Card-Unlocked-150Mbps-Dongle-i.287338238.3544783624
- GET of the modem gateway serves an Android-based management UI titled `UFI-JZ_V3.0.0`. Earlier HEAD 404 did not mean there was no UI.
- Its public JavaScript defines POST APIs under `/api/`, using URL-encoded form bodies. The APN UI sends an empty object to `system/getCurrentApn`, and `{mcc,mnc,name,apn}` to `system/addApn`.
- Dashboard request `wifi/getWifiInfo` with `lang=2` showed model UFI, SIM identifier present (value not printed), SIM slot 1, mobileData=1 and signal -101 dBm. This does not prove registration or working internet.
- Current APN initially returned code 0, no data. Backed up this exact response to local `work/modem-apn-before-20261002-133227.json` (0600).
- Saved `name=circles`, `apn=sunsurf`, `mcc=525`, `mnc=03` using the modem's APN API. Save returned code 1; immediate readback confirmed all four fields. These values follow Circles.Life's official support instructions: https://circlesasiasupport.zendesk.com/hc/en-us/articles/900000254083-How-do-I-set-my-APN-Settings-to-enable-my-roaming-data
- Did not alter the modem's login password, Wi-Fi settings, identity, firmware, or Pi network preference. Did not reboot.
- A request to the operator API with unspecified parameters dropped the connection and the management HTTP service briefly stopped responding. Do not repeat that request without first reading the correct UI request schema.
- Post-change internet testing was blocked: new SSH connections timed out, and the existing modem tunnel stopped responding. Mac now reports 192.168.0.100 via gateway 192.168.0.1, while roverpi.local resolves to its last 192.168.1.1 address. An observed link-local IPv6 SSH probe also failed. Do not claim cellular internet has been verified after the APN change.
- Asked user to temporarily reconnect the Mac to HOME_WIFI_SSID to finish verification and remote-access setup. This is a setup dependency, not a requirement for eventual cellular operation.

## Remote robot control findings

- StampNote Live tunnel is https://stampnote-omega.vercel.app/live-tunnel . Its existing driving panel embeds the entered address in an iframe. Its `src/services/robot-control-url.js` currently accepts IP literals only and rejects domain names; an HTTPS remote-control hostname would need application changes.
- On the Pi, only SSH port 22 and localhost Chromium CDP port 9222 were listening. No robot driving web service was identified, and tailscale/cloudflared/ngrok were absent.
- Remote driving is NOT configured. Still need the user's current driving app/address or controller details, working cellular internet, an authenticated remote connection, and appropriate StampNote integration. Do not expose CDP or issue movement commands while diagnosing networking.

## After the Mac reconnected to HOME_WIFI_SSID

- Mac returned to 192.168.1.5 via gateway 192.168.1.254. mDNS briefly failed, then rediscovered roverpi.local at 192.168.1.1. ARP confirmed the rover's known Wi-Fi MAC. IPv4 SSH works; use `work/rover-ssh.exp -4` to avoid an unsuccessful link-local IPv6 connection attempt.
- Pi uptime confirmed it had not rebooted. StampNote boot/display/browser services are active.
- CDP verified the exact robotic-control page, status `Streaming video — Live tunnel can share this camera.`, and live, unpaused C270 video at 1280x720. Currently using Wi-Fi.
- Modem still enumerates as 05c6:9024, now USB device 001/008 at physical path `1-1.4.3`. Its RNDIS interface usb0 has no IPv4 address. NetworkManager reports disconnected following repeated DHCP timeouts.
- Kernel logs show modem disconnect/re-enumeration at 13:32:40, shortly after saving the APN, then repeated `NETDEV WATCHDOG ... transmit queue 0 timed out` messages. This supports a modem/USB networking stall; it does not prove the SIM or APN is invalid.
- Explicit DHCP retry failed. A temporary 192.168.42.133/24 address was added only for probing the previously known gateway, which was unreachable; the temporary address was removed in a finally block. Saved profiles and priority were not changed.
- Reset only the vendor/product-verified modem via `/usr/bin/usbreset 001/008`; reset returned success, but the following DHCP retry still failed.
- Unbound/rebound only its `rndis_host` interface `1-1.4.3:1.0`, then retried DHCP once. Still failed. No Pi reboot or camera reset performed.
- Modem USB power control is `on` and runtime state `active`; Pi throttling flag is 0x0. USB interface showed zero RX/TX after reinitialization. No evidence justifying power-saving configuration changes.
- Asked user to physically unplug only the modem for 10 seconds and reconnect, preferably directly to a Pi USB port. Awaiting that action before retesting. Also awaiting the driving app/address or confirmation that movement control has never been configured.

## Diagnosis after the physical reconnect

- USB modem includes an ADB diagnostic interface. Installed official Debian `adb`
  and its dependencies on the Pi; used a root-owned, localhost-only ADB server
  because the existing USB device node lacked rover-user access. The Android
  shell itself remained uid 2000, not root. No rooting or firmware changes.
- Android 4.4.4 / API 19 UFI firmware reports SIM READY, operator Circles,
  numeric operator 52503, LTE, mobile data enabled. Its rmnet_data0 interface had
  an upstream address/default route and successfully pinged 1.1.1.1. Thus the
  saved Circles APN and cellular connection work inside the modem.
- The missing Pi DHCP lease was explained by Android USB tethering being off:
  rndis0 was DOWN/unaddressed and listed as available rather than tethered.
- Temporarily forwarded Pi localhost:4850 to modem HTTP port 80 through ADB to
  confirm the saved APN. APN readback remained circles/sunsurf/525/03.
- The vendor binder transaction numbers differ from stock Android. Extracted
  actual IConnectivityManager constants from the modem framework.odex. The
  vendor setUsbTethering transaction is 38. Calling it from ADB shell failed
  with CHANGE_NETWORK_STATE permission denied; no attempt to bypass that
  boundary was made. A normal app can request this network permission.

## Direct USB connection and USB-sharing helper

- User moved the modem directly to Pi USB port path 1-1.4. It reappeared as
  05c6:9091 in diag,serial_smd,rmnet_bam,adb mode (wwan0), not USB tethering.
  SIM remained READY with LTE upstream. Therefore direct attachment alone
  did not restore Pi internet access. The webcam and old hub were also removed.
- Built a minimal app, `local.rover.usbtether` (Rover USB Link), from the source
  in `work/modem-usb-helper/`. It uses normal ACCESS_NETWORK_STATE,
  CHANGE_NETWORK_STATE, and RECEIVE_BOOT_COMPLETED permissions. Its receiver
  requires sender permission DUMP, allowing system/diagnostic-shell triggers.
  It uses ConnectivityManager.setUsbTethering(true), with an already-tethered
  guard, on BOOT_COMPLETED, connected USB_STATE, and an explicit ENABLE action.
  It has no internet permission, credentials, or motor controls.
- Build tools installed from official Debian repositories: aapt, apksigner,
  libsmali-java and Java runtime/dependencies. No existing packages upgraded.
  Compiled manifest against the modem's own framework-res.apk. Verified APK
  signature including v1 compatibility with Android 4.4.4, and exact permissions.
- Pi source/build path: `/home/rover/modem-usb-helper/`; signing material is in
  its private signing directory (0700, files 0600). Local APK copy:
  `work/modem-usb-helper/rover-usb-link.apk`. Keep the signing key for updates.
- `adb -s 0 install .../rover-usb-link.apk` succeeded; triggered with
  `am broadcast --include-stopped-packages -a local.rover.usbtether.ENABLE
  -n local.rover.usbtether/.EnableReceiver`.
- Modem switched to USB Ethernet, rndis0 became TetheredState, lastError=0.
  Pi DHCP obtained 192.168.42.133, gateway/DNS 192.168.42.129. Existing NM
  cellular route metric 50 selected usb0; Wi-Fi remains metric 600.
- `curl -4 --interface usb0 ... https://stampnote-omega.vercel.app/robotic-control`
  returned HTTP 200, source 192.168.42.133, ~0.52 s. A separate HTTPS request
  to raspberrypi.com returned HTTP 403 from the website, still proving an
  external TLS/HTTP response over the modem. Do not describe that 403 as 200.
- Package manager confirms installed=true, stopped=<PRIVATE_VALUE_NOT_PUBLISHED>, notLaunched=<PRIVATE_VALUE_NOT_PUBLISHED>,
  enabled/default, required permissions and both boot/USB intent filters.
  This proves configuration, not a successful cold boot. No Pi reboot performed.
- All three StampNote services remain active. Webcam was absent, and user
  answered “Not yet” when asked if it had been reconnected. Do not claim the
  video stream is currently live. Reconnect camera, then verify/recover page.
- Direct USB operation plus a software change succeeded, so the extension/hub
  is not proven faulty. Pi 4 USB total budget is 1.2 A across all ports; an
  externally powered hub may help if peripheral demand exceeds that budget.
  Source: https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#power-supply
- At the direct-connection check throttled=0xe0000, temperature 65.7 C: past
  thermal/frequency throttling flags, with no current throttle or undervoltage
  bits set. This does not measure the voltage delivered at the modem.

Helper removal (if ever requested): `adb -s 0 uninstall local.rover.usbtether`.
This removes future auto-enabling; it does not disconnect an existing tether.

## Final shared-hub configuration and verification (15:07 SGT)

- User needs the hub for physical clearance and reconnected both devices to it.
  Confirmed webcam path 1-1.4.1 and modem 1-1.4.3 under the same Genesys hub.
  Both enumerate at 480 Mbit/s (USB 2.0); this is expected for these devices.
- The modem initially booted into diagnostic mode, then changed to RNDIS through
  its helper. Initial helper logs included a MANAGE_USB denial from the firmware's
  mode-switch API. No signature permission was granted or bypassed. Later normal
  calls reported success, but a subsequent USB re-enumeration left rndis0 available
  and untethered again. `setUsbTethering(true)` alone was therefore insufficient.
- Helper v1.1 (versionCode 2) now first calls ConnectivityManager.tether(interface)
  when an available USB/rndis interface exists. This API uses the app's ordinary
  CHANGE_NETWORK_STATE permission. Result 0 was confirmed and rndis0 became
  TetheredState. The existing signing identity was preserved; installed with -r.
- Retried NM connection 75a1216a-9d1a-30cd-8aca-ace5526ec021 after its earlier DHCP
  failures. Obtained 192.168.42.133 immediately and cellular HTTPS returned 200.
- Added `/usr/local/sbin/rover-cellular-usb`, with root-owned systemd unit and
  `rover-cellular-usb.timer` in `/etc/systemd/system/`. Timer enabled/active;
  starts 20 seconds after boot and checks every 30 seconds. Final service result
  success, ExecMainStatus=0. Existing files are backed up before replacement under
  `/var/backups/rover-cellular/<timestamp>/`.
- Recovery script leaves an addressed usb0 alone. Otherwise it verifies the UFI
  modem's 05c6:{9024,9091}, serial 0 identity, uses private localhost ADB port 5038
  to broadcast ENABLE to the helper, then closes the diagnostic server. It retries
  the existing NM USB profile only when disconnected/failed, not while connected
  or already acquiring an address. It is not an upstream-internet health monitor.
- The webcam's original browser track was ended after unplugging, despite a stale
  “Streaming video” status. Ran `rover-stream restart`, preserving profile/login.
  Subsequent CDP checks found exact /robotic-control, live C270 track, 1280x720,
  paused=<PRIVATE_VALUE_NOT_PUBLISHED>, video time increasing from 162.54 to 602.48 seconds, and the
  “Streaming video — Live tunnel can share this camera.” status.
- At 15:07:23 SGT: default route to 1.1.1.1 is usb0 via192.168.42.129; both normal
  curl and `curl --interface usb0` to the exact robotic-control URL returned HTTP
  200 with local source192.168.42.133. Thus ordinary traffic is cellular, not just
  the explicit interface-bound probe. Wi-Fi remains available at metric600.
- No USB disconnect, watchdog, or undervoltage messages in the final four-minute
  kernel-log window, while camera capture was live. This is a short functional
  check, not a claim of long-term hub stability or measured peripheral power.
- No diagnostic listeners remained on ports4850/5037/5038; CDP stayed localhost9222.
  No Pi reboot performed. Updated APK/source are retained locally and on the Pi.
