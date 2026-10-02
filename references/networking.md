# Cellular, home Wi-Fi and wheel-controller networking

## Topology

| Link | Pi interface | Purpose / last observed addressing |
|---|---|---|
| Home Wi-Fi | wlan0 | Owner's private SSID; last Pi192.168.1.1, gateway192.168.1.254; metric600 |
| Cellular UFI modem | usb0 | Pi192.168.42.133, gateway192.168.42.129; metric50 |
| Wheel-controller AP | roverctl | AP UGV at192.168.4.1, Pi DHCP192.168.4.4; never a default route |

The controller's station IP was192.168.0.82 while the home LAN was192.168.1.x.
It was not reachable through that home LAN. A virtual managed interface on the Pi's
existing Wi-Fi radio connects directly to the controller's AP, while wlan0 retains
home connectivity. The installed `rover-controller-wifi` helper creates that
interface; `rover-wheel-direct` is a private NetworkManager profile with autoconnect,
never-default and no supplied DNS. Its AP credentials are intentionally not included.
Radio channel compatibility remains relevant because both interfaces share hardware.

Controller firmware serves `UGV01_BASE_WEB` at192.168.4.1. It is a separate controller,
not the Pi's cellular gateway or the modem hotspot.

## Cellular preference

Provider: Circles.Life Singapore. SIM was activated and worked in a phone.
The last saved APN was name `circles`, APN `sunsurf`, MCC525, MNC03; verify with the
provider for a different SIM/plan. Existing NetworkManager profile `netplan-eth0`
(UUID75a1216a-9d1a-30cd-8aca-ace5526ec021) has metric50. Home Wi-Fi uses600.
The scripts target this known profile; adjust deliberately on a different Pi.

```sh
ip -br -4 addr
ip -4 route
ip -4 route get 1.1.1.1
nmcli -f NAME,DEVICE,TYPE connection show --active
lsusb -t
```

A lower route metric only prefers an available interface. It does not prove working
cellular internet and is not an internet-health failover system. Use a small
interface-bound HTTPS request when verifying real cellular traffic.

## UFI USB-tether recovery

This generic USB router is an Android4.4.4 UFI modem, not a typical AT-command modem.
Known USB IDs:05c6:9024 normal RNDIS and05c6:9091 diagnostic mode; serial0.
No ttyUSB/cdc-wdm interface was present during diagnosis. Do not assume ModemManager
or firmware flashing is appropriate.

The source and signed helper APK are under [cellular](../cellular/README.md).
The helper uses ordinary Android network APIs to enable USB tethering at boot and
USB connection. Its explicit receiver requires the sender's DUMP permission. It
does not require modem root or grant itself privileged USB permissions.

The Pi's root timer runs20 seconds after boot and every30 seconds. It leaves an
already-addressed usb0 alone; otherwise it verifies the expected USB identity and
UFI model, briefly uses localhost-only ADB port5038, triggers the existing helper,
closes ADB and retries only disconnected/failed DHCP. Do not leave diagnostic ADB
servers listening or run competing ADB sessions during this recovery.

The APK's signing key is private and not included. Rebuilding with a different key
will not update the installed APK in place. Preserve the existing private signing
material or plan a deliberate reinstall; do not publish it.

## USB hub and battery findings

Webcam and modem share a Genesys expansion hub because of mechanical clearance.
At the last session, the modem repeatedly disappeared and re-enumerated; software
then switched the default route between cellular and Wi-Fi. This was below the
Cloudflare layer. The exact cause was not established.

Check kernel timestamps, modem uptime if accessible, cables, hub power and the
owner's physical reconnect activity. USB power/control was already `on`; do not
blindly change power-saving flags. A zero Pi undervoltage flag does not prove the
modem's own supply is stable.

The Pi4's USB power budget is shared across ports; a powered hub is a useful
isolation test if demand exceeds it. Temperature reached84.7°C, and controller
battery telemetry fell from about11.3V to8.4V before the owner reported an empty
battery. Recharge and recheck before attributing all drops to firmware or carrier.

References:
- [Raspberry Pi power and cooling](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html)
- [Circles.Life APN instructions used during setup](https://circlesasiasupport.zendesk.com/hc/en-us/articles/900000254083-How-do-I-set-my-APN-Settings-to-enable-my-roaming-data)

## Later powered-on check — 3 October, about 04:00 SGT

Cellular had an IP address and retained metric 50, but an interface-bound HTTPS
request timed out after eight seconds. The same HTTPS target over wlan0 returned
200 in about 0.18 seconds. Cloudflared reported zero ready connections, network
unreachable errors and edge TCP timeouts; restarting it did not restore service
during this check. The local authenticated control UI, session and T130 battery
query still returned 200. This distinguishes a broken cellular internet path from
the new UI or motion guard. No APN, route preference or radio firmware was changed.
