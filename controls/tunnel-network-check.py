#!/usr/bin/python3
"""Reconnect this rover's tunnel after a cellular/Wi-Fi route change."""
import json
import os
from pathlib import Path
import subprocess
import time
from urllib.error import URLError
from urllib.request import urlopen

UNIT = "rover-controls-named-tunnel.service"
state_path = Path(os.environ["XDG_RUNTIME_DIR"]) / "rover-controls-network.json"


def run(*args):
    return subprocess.run(args, text=True, capture_output=True, timeout=5)


def main():
    status = run("systemctl", "--user", "show", UNIT, "-p", "ActiveState", "--value")
    if status.returncode or status.stdout.strip() != "active":
        return  # The unit's startup timeout and restart policy handle startup.
    route_result = run("ip", "-j", "-4", "route", "get", "1.1.1.1")
    if route_result.returncode:
        return
    route = json.loads(route_result.stdout)[0]
    current = {key: route.get(key) for key in ("dev", "gateway", "prefsrc")}
    if not current["dev"]:
        return
    # A modem can disappear and return with the same address between polls.
    # Its Linux interface index still changes, so do not treat that as the
    # existing connection whose TCP sockets cloudflared can continue using.
    try:
        current["ifindex"] = int((Path("/sys/class/net") / current["dev"] / "ifindex").read_text())
    except (FileNotFoundError, ValueError):
        return  # The interface disappeared during this check; retry next tick.
    try:
        previous = json.loads(state_path.read_text())
    except (FileNotFoundError, ValueError):
        previous = {}
    ready = False
    try:
        with urlopen("http://127.0.0.1:20242/ready", timeout=3) as response:
            ready = response.status == 200
    except (URLError, TimeoutError, OSError):
        pass
    now = time.monotonic()
    failure_since = None if ready else previous.get("failure_since") or now
    previous_route = previous.get("route")
    changed = previous_route is not None and (
        any(previous_route.get(key) != current[key] for key in ("dev", "gateway", "prefsrc"))
        or ("ifindex" in previous_route and previous_route["ifindex"] != current["ifindex"])
    )
    stalled = failure_since is not None and now - failure_since >= 60
    if changed or stalled:
        result = run("systemctl", "--user", "--no-block", "try-restart", UNIT)
        if result.returncode:
            raise RuntimeError("Unable to request tunnel restart")
        print("Restart requested: " + ("internet route changed" if changed else "tunnel disconnected for 60 seconds"))
        failure_since = None
    state_path.write_text(json.dumps({"route": current, "failure_since": failure_since}))


if __name__ == "__main__":
    main()
