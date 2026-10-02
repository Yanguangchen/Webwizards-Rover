#!/usr/bin/env python3
"""Authenticated, loopback-only relay for this rover's existing UGV controls."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import Request, urlopen
from motion import MotionError, MotionGuard

STAMP_ORIGIN = "https://stampnote-omega.vercel.app"
LANDING = b'''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rover controls</title><style>
body{margin:0;min-height:100vh;display:grid;place-items:center;background:#101a21;color:#eff5f6;font:16px system-ui}
main{width:min(85vw,360px);padding:32px}h1{font-size:28px}p{color:#b3c7cd;line-height:1.5}
input,button{box-sizing:border-box;width:100%;padding:14px;border-radius:9px;font:inherit;margin:6px 0}
input{background:#1b2b35;color:white;border:1px solid #52707e}button{background:#88dfc0;color:#0b2821;border:0;font-weight:650}
#status{min-height:48px}</style><main><h1>Rover controls</h1>
<p>Open your private link or enter the control key.</p>
<form id="unlock"><label for="key">Control key</label><input id="key" type="password" autocomplete="off" required>
<button type="submit">Connect to rover</button></form><p id="status" role="status"></p></main>
<script data-cfasync="false">
const field=document.querySelector('#key'),status=document.querySelector('#status');
async function connect(key){status.textContent='Connecting to rover...';
try{const response=await fetch('/origin/',{headers:{'X-Rover-Key':key},cache:'no-store'});
if(!response.ok){status.textContent=response.status===401?'The control key is incorrect.':'The rover controller is unavailable. Try again when it is connected.';return;}
const html=await response.text();document.open();document.write(html);document.close();
}catch{status.textContent='Connection failed. Check the rover is online and try again.';}}
document.querySelector('#unlock').addEventListener('submit',e=>{e.preventDefault();connect(field.value.trim());});
const key=new URLSearchParams(location.hash.slice(1)).get('key');if(key){field.value=key;connect(key);}
</script></html>'''


def authenticate(candidate, expected):
    return secrets.compare_digest(candidate.encode("utf-8"), expected.encode("utf-8"))


def controls_html(key):
    config = {'maxSpeed': MotionGuard.MAX_SPEED, 'fullSpeed': MotionGuard.FULL_SPEED,
              'defaultRate': MotionGuard.DEFAULT_RATE}
    # Only our compact driving UI is served; the stock console/settings are absent.
    source = Path(__file__).with_name('motion-client.js').read_text()
    source = source.replace('KEY_VALUE', json.dumps(key).replace('<', '\\u003c'))
    source = source.replace('CONFIG_VALUE', json.dumps(config))
    html = Path(__file__).with_name('controls.html').read_text()
    return html.replace('<!-- MOTION_SCRIPT -->',
                        '<script data-cfasync="false">' + source + '</script>').encode('utf-8')


class RelayServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, upstream, key, enable_drive=False):
        self.upstream = upstream.rstrip("/")
        self.key = key
        self.motion = MotionGuard(self.send_motion, enabled=enable_drive)
        super().__init__(address, RelayHandler)

    def send_motion(self, command):
        target = self.upstream + '/js?' + urlencode({'json': json.dumps(command, separators=(',', ':'))})
        with urlopen(Request(target), timeout=0.25) as response:
            if response.status != 200:
                raise OSError('Controller command failed')
            response.read(4096)


class RelayHandler(BaseHTTPRequestHandler):
    server_version = "RoverControls/1.0"

    def setup(self):
        super().setup()
        self.connection.settimeout(10)

    def log_message(self, *_):
        # Controller queries can include Wi-Fi credentials. Never log URLs/keys.
        pass

    def respond(self, code, body, content_type="text/plain; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'self' " + STAMP_ORIGIN)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def do_GET(self):
        path = urlsplit(self.path)
        if path.path == "/" and not path.query:
            return self.respond(200, LANDING, "text/html; charset=utf-8")
        if path.path not in ("/origin/", "/origin/js"):
            return self.respond(404, b"Not found")
        if not authenticate(self.headers.get("X-Rover-Key", ""), self.server.key):
            return self.respond(401, b"Control key required")
        if path.path == "/origin/":
            if path.query:
                return self.respond(400, b"Invalid request")
            return self.respond(200, controls_html(self.server.key), "text/html; charset=utf-8")
        else:
            if len(path.query) > 8192:
                return self.respond(400, b"Command too large")
            try:
                query = parse_qs(path.query, strict_parsing=True)
                if set(query) != {"json"} or len(query["json"]) != 1:
                    raise ValueError()
                command = json.loads(query["json"][0])
                if not isinstance(command, dict) or type(command.get("T")) is not int:
                    raise ValueError()
                if command['T'] in (1, 11, 13, 136):
                    if command == {'T': 1, 'L': 0, 'R': 0}:
                        self.server.motion.request('stop', {})
                        return self.respond(200, b'null', 'application/json')
                    return self.respond(409, b'Reload controls: raw wheel commands are disabled; use motion leases')
                target = self.server.upstream + "/js?" + urlencode({"json": json.dumps(command, separators=(",", ":"))})
            except (ValueError, KeyError, TypeError):
                return self.respond(400, b"Invalid command")
        try:
            with urlopen(Request(target, headers={"Accept": "*/*"}), timeout=4) as response:
                body = response.read(1_000_001)
                if len(body) > 1_000_000:
                    raise ValueError("Response too large")
            content_type = "application/json; charset=utf-8"
            return self.respond(200, body, content_type)
        except (HTTPError, URLError, TimeoutError, OSError, ValueError):
            return self.respond(502, b"Rover controller unavailable")

    def do_HEAD(self):
        if self.path == "/":
            return self.respond(200, LANDING, "text/html; charset=utf-8")
        return self.respond(405, b"Method not allowed")

    def do_POST(self):
        if not self.path.startswith('/motion/') or self.path.count('/') != 2:
            return self.respond(404, b'Not found')
        if not authenticate(self.headers.get('X-Rover-Key', ''), self.server.key):
            return self.respond(401, b'Control key required')
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 2048:
                raise ValueError()
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError()
            action = self.path.removeprefix('/motion/')
            result = self.server.motion.session() if action == 'session' else self.server.motion.request(action, data)
            return self.respond(200, json.dumps(result).encode(), 'application/json')
        except MotionError as error:
            return self.respond(error.status, json.dumps({'error': error.message}).encode(), 'application/json')
        except (ValueError, TypeError):
            return self.respond(400, b'{"error":"Invalid control request"}', 'application/json')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream", default="http://192.168.1.10")
    parser.add_argument("--port", type=int, default=8877)
    parser.add_argument("--key-file", required=True)
    parser.add_argument("--enable-drive", action="store_true")
    args = parser.parse_args()
    key = Path(args.key_file).read_text().strip()
    if len(key) < 32:
        raise SystemExit("Control key must be at least 32 characters")
    server = RelayServer(("127.0.0.1", args.port), args.upstream, key, enable_drive=args.enable_drive)
    server.motion.start()
    server.serve_forever()
