> Historical diagnostic record. Later entries and the root README take precedence. Credentials and account emails are omitted. Local screenshot paths mentioned below are not published.

# App status and permanent control address — 3 October 2026

## Confirmed camera/app state

SSH to Pi192.168.1.1 with HostKeyAliasroverpi.local. All five user services active
(stream boot, display, browser, controls relay, controls tunnel). Cellular default
usb0; direct controller roverctl route4/24 intact. No app restart this turn.

Read-only localhost CDP diagnostic over user-requested SSH confirmed exact
https://stampnote-omega.vercel.app/robotic-control, signed-in DOM label, live C270
track1280x720 unpaused. Video currentTime advanced1322.45 to1570.33seconds. Page
claims Streaming video — Live tunnel can share this camera, but that status is
misleading about actual publication success.

Browser console repeatedly logs Firestore12.17.1 FirebaseError code
resource-exhausted, Quota exceeded, followed by maximum backoff. This occurs from
17:21 through17:43UTC and is the observed publication blocker.

Firebase console for stampnote-eedcd was accessible in Chrome. Firestore Usage
shows Spark/no-cost plan, writes20K, reads2.9K, deletes2, and project-exceeded
no-cost-limits alert. No billing plan change or Upgrade click performed.
Screenshot work/firestore-quota-2026-10-03.jpg. Usage tab kept open as deliverable.

Deployed src/services/live-tunnel.js verified PICTURE_MS550 and heartbeat8000.
startPictureRelay runs whenever publishing begins, even without viewers. Thus
continuous database image writes can exhaust20,000daily writes; theoretical
maximum about157,000image writes/day plus10,800heartbeats, actual rate depends on
capture/write latency. No cloud/app code changed in this status-check turn.
Firestore free quotas reset around midnightPacific (~15:00SGT on3October2026).
Repeated restarts do not fix exhausted server-side quota. Follow-up fixes should
reduce unnecessary image writes, surface publication failures accurately, and
recover/retry publication after quota clears; prefer WebRTC for live video rather
than high-frequency Firestore images. Turning on paid billing needs user approval.

## Static control link status

Current marine-charges-surplus-excited.trycloudflare.com is a Quick Tunnel,
explicitly temporary. Existing private access link remains in mode0600 file
work/rover-private-control-link.txt. No tunnel changes this turn.

Cloudflare named/remotely managed tunnel plus published application hostname can
provide a permanent domain, serving same authenticated127.0.0.1:8877 relay; no
need for a public cellular IP. Cloudflare dashboard is signed out. Opened login
page and marked handoff; did not create account, accept terms or modify DNS.
Asked user which domain they own (Cloudflare, elsewhere, or no domain). No answer
yet. Do not assume a domain or purchase one. If no domain, consider a provider's
assigned stable hostname or an authenticated app-level stable entrypoint, after
confirming account/infrastructure choices.

References:
https://firebase.google.com/docs/firestore/quotas
https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/
https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/get-started/create-remote-tunnel/
