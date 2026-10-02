> Historical diagnostic record. Later entries and the root README take precedence. Credentials and account emails are omitted. Local screenshot paths mentioned below are not published.

# Permanent rover controls hostname

## Final verification, approximately 02:38 SGT (supersedes earlier limitations)

- Home-router DNS finally resolved rover.webwizardsg.com normally. Flushed only
  Mac local DNS cache. No DNS settings changed; earlier approval question is
  no longer needed.
- Added tunnel-network-check.py and enabled user timer
  rover-controls-network-check.timer (15-second interval, starts after boot).
  It restarts the named tunnel when default IPv4 device/gateway/source changes,
  or readiness remains failed for 60 seconds. Fixed metrics address to
  127.0.0.1:20242. Systemd units verified, Python compiled, oneshot Result=success
  ExecMainStatus=0, route baseline usb0, failure_since=null. No full reboot or
  deliberate network disconnect test performed.
- Public check over actual cellular using normal DNS: landing200, missing and
  wrong key401, authenticated UGV HTML200, read-only T130200. Final complete check
  succeeded after all tunnel connections had established.
- Browser showed static controls but no telemetry. Found domain-wide Cloudflare
  Rocket Loader rewriting inline scripts to non-executable types. Applied only
  to the relay HTML: data-cfasync="<PRIVATE_VALUE_NOT_PUBLISHED>" on landing, injected auth shim, and
  original controller scripts, following official Rocket Loader documentation.
  Backed up Pi relay before replacement; compiled Python and restarted relay.
  No domain-wide website settings changed. This fixed controller initialization.
- StampNote saved private URL with the existing #key fragment. A bare hostname
  had appeared in the field during user interaction; restored the required
  private URL. Fresh iframe then showed real battery11.28V, RSSI-35, live roll,
  pitch, temperature68.89C, controller IP192.168.0.82 and expected MAC. No motors
  were moved. Keep private link/key out of public docs/repositories.
- Retiring old Quick Tunnel after successful browser verification; its unit is
  backed up in ~/.config/rover-controls/quick-tunnel-before-static.service.
- The earlier USB modem drops remain an observed reliability concern. Recovery
  and tunnel route handling are improved, but physical cause is unproven. Pi
  throttled=0x0 during inspection; this does not measure USB hub/device voltage.
- Live video is still blocked by Firebase quota, independently of motor controls.
  User asked about Blaze but did not authorize/complete a billing upgrade in this
  task. No paid settings changed.

Reference for script exclusion:
https://developers.cloudflare.com/speed/optimization/content/rocket-loader/ignore-javascripts/

## Implemented update, approximately 02:23 SGT

IMPORTANT CURRENT LIMITATION (02:26-27): external verification is intermittent,
not complete. After the successful 200/401/controller/telemetry check, later
checks returned Cloudflare 502 and 530/1033. At 02:26:14 local relay was HTTP200
and /ready reported four connections; at 02:26:42-46 Mac and Pi requests both
returned Cloudflare530. Do not report the permanent endpoint as currently
reliably working solely from local /ready or dashboard Healthy. Asked whether
the user is physically unplugging/moving the modem; awaiting reply. No whole-Pi
reboot, paid billing change, or Mac Wi-Fi DNS change was performed.

Later verification: the modem dropped again around 02:23, causing a brief public
1033 error. The named IPv4 tunnel recovered automatically (no further restart)
and /ready returned 200 with four connections. At the last network check,
cellular usb0 was again the preferred default and the USB recovery timer was
active. Therefore modem instability remains unresolved; do not claim that the
initial disconnect was permanently fixed. No new tunnel watchdog was installed
because cloudflared recovered its connections itself after the route change.

The Mac DNS change remains pending user approval. Its current Wi-Fi DNS setting
is automatic (networksetup reported no configured DNS servers). If approved,
set 1.1.1.1 and 1.0.0.1; rollback is `networksetup -setdnsservers Wi-Fi Empty`.

- User signed in to Cloudflare. Account ddbf4bfaeba6db53b96dfb7583c51a88.
- Domain active on Free plan. Inspected all 18 existing DNS records; no rover
  record existed. Root/www and email records were not modified.
- Created remotely managed tunnel rover-controls, ID
  d3fc6e2d-a0a8-4ef5-976f-58bf1f3ba7b6. Connected Pi roverpi, linux_arm64,
  cloudflared 2026.9.3, dashboard Healthy.
- Published rover.webwizardsg.com -> http://127.0.0.1:8877, with default 404
  fallback. Cloudflare created its proxied CNAME to the tunnel's cfargotunnel.com
  hostname. Authoritative DNS, 1.1.1.1, and 8.8.8.8 all return Cloudflare edge IPs.
- Installed enabled user unit rover-controls-named-tunnel.service. Private token
  at ~/.config/rover-controls/tunnel-token, mode 0600. Linger=yes. Unit uses
  Type=notify, 90-second startup timeout, Restart=on-failure, unlimited startup
  retry interval, HTTP/2, and --edge-ip-version 4.
- IPv4 was selected after an actual modem disconnect left the original IPv6
  connector retrying without an IPv6 route on home Wi-Fi. Restart validated on
  Wi-Fi and then on restored cellular; final observed PID 8084 registered four
  IPv4 HTTP/2 connections to Singapore edges at 02:21:03-05.
- Tested public HTTPS against the verified edge IP while retaining TLS hostname
  validation: landing 200, missing/wrong key 401, authorized controller HTML 200,
  T130 telemetry 200. No motion commands. Pi relay remains loopback-only.
- Updated StampNote's visible Robot controls URL or IP to the permanent private
  URL, keeping its existing key. Saved private URL in work/rover-private-control-
  link.txt (0600); old URL in work/rover-private-control-link.before-static.txt.
- Browser verification remains blocked by home router DNS at 192.168.1.254,
  which returns synthetic NXDOMAIN with SOA nxd.local/need.to.know.only and TTL
  600. Do not claim this is definitely a normal cache or will clear by a known
  time. Mac local DNS flush did not fix it. Wi-Fi DNS is automatic. Asked user
  whether to change this Mac's Wi-Fi DNS to 1.1.1.1/1.0.0.1; no change yet.
- Old Quick Tunnel remains enabled/active pending final browser verification.
  Stop/disable it after migration is verified. Do not stop the relay.
- Cloudflare route proof screenshot: work/rover-permanent-cloudflare-route-
  2026-10-03.jpg. Dashboard and StampNote tabs marked deliverable.

## Modem interruption during this work

At approximately 02:13 the UFI USB modem repeatedly disconnected and enumerated
as 05c6:9091 diagnostic mode. Existing recovery service failed with timeout and
missing broadcast acknowledgment while the device was reconnecting. Webcam
remained attached. No Pi or modem reboot was requested or performed.

Read-only ADB check confirmed model UFI, boot complete, existing helper installed.
Triggered the same approved helper with local.rover.usbtether.ENABLE using
localhost-only diagnostic port 5039. Logs initially showed firmware MANAGE_USB
permission denial, then ordinary helper calls returned result 0 and reported
USB tethering already enabled. No rooting/permission grants/firmware changes.
Port 5039 was closed in a trap; the recovery timer was temporarily stopped during
this diagnostic and restarted in the same trap. Final listener check found no
5038/5039 diagnostic servers.

Cellular restored: usb0 192.168.42.133, default metric 50, Wi-Fi fallback metric
600, forced usb0 HTTPS to StampNote returned 200. This is functional recovery,
not a diagnosis of why the modem initially disconnected or proof of long-term
hub/power stability.

## Live-video and billing questions

Rechecked Pi at 02:05: signed in to exact robotic-control URL; live C270 video
1280x720, unpaused, currentTime 2642.92sec. Firestore quota errors continued
through 02:05. Explained daily 20K writes and approximate 15:00 SGT reset today.
User asked whether they can upgrade billing. Explained Blaze pay-as-you-go,
free allowance retained, extra usage charged, and budget alerts are not a hard
cap. Provided Firebase console link. No billing plan or payment changes made.

## Original preparation (superseded where noted above)

User supplied webwizardsg.com, registered with Namecheap and managed/proxied
through Cloudflare. Public DNS verified bristol.ns.cloudflare.com and
brad.ns.cloudflare.com. No registrar or nameserver migration is needed.

Proposed hostname: rover.webwizardsg.com (not created or live yet).
Proposed Cloudflare remotely managed tunnel: rover-controls; check account for
existing tunnels and DNS records before creating anything.
Published service: http://127.0.0.1:8877 on the Raspberry Pi.
Keep the existing relay's access key, fragment unlock, and authorization checks.

The current relay and Quick Tunnel are active and enabled. SSH verified relay
HTTP 200, internet route via cellular usb0, controller route via roverctl. No
service or DNS changes have been applied in this turn.

Cloudflare dashboard is signed out. User asked to sign in in the open Chrome
tab; the tab is marked handoff. Account login is the current prerequisite.

Prepared local unit: rover-public-control/rover-controls-named-tunnel.service.
It is only a draft, not installed. Type=notify plus TimeoutStartSec=90 is intended
to restart a connector that gets stuck during startup instead of considering it
healthy solely because its process exists. Verify ready notification and restart
behavior after installing. Do not reboot without user authorization.

Next steps after sign-in:
1. Inspect domain status, current DNS records, tunnels, and any applicable rules.
2. Create or reuse a scoped remotely managed tunnel and publish only the relay
   as rover.webwizardsg.com. Avoid changes to root/www/mail or other services.
3. Store the tunnel token privately in the Pi config directory (0700 directory,
   0600 file); never print token in tool outputs or shared notes.
4. Back up existing files before modifying. Install the named service alongside
   the current Quick Tunnel so rollback remains available during verification.
5. Verify public HTTPS, unauthenticated 401, authenticated UI, and read-only T130
   telemetry. Do not send wheel/motor commands.
6. Update StampNote's saved robot controls URL to the new hostname, preserving
   the private access-key fragment. Verify the embedded controls.
7. Verify automatic startup is enabled and service restart keeps the same URL.
   Stop/disable the old Quick Tunnel only after successful migration. Keep its
   backed-up unit available for rollback (a restarted Quick Tunnel gets a new URL).

Official documentation retrieved:
- https://developers.cloudflare.com/tunnel/get-started/
- https://developers.cloudflare.com/tunnel/reference/tunnel-tokens/
- https://developers.cloudflare.com/tunnel/reference/run-parameters/

The separate StampNote live-recording outage was diagnosed as Firestore write
quota exhaustion; a permanent motor-controls hostname does not fix that issue.
