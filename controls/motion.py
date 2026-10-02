"""Short, ordered motion leases. Network requests never directly drive motors."""
import math
import secrets
import threading
import time


class MotionError(Exception):
    def __init__(self, status, message):
        self.status, self.message = status, message


class MotionGuard:
    LEASE_SECONDS = 0.5
    FULL_SPEED = 0.5
    DEFAULT_RATE = 0.3
    MAX_SPEED = 0.25
    WATCHDOG_MS = 350

    def __init__(self, send, clock=time.monotonic, enabled=False):
        self.send, self.clock = send, clock
        self.lock = threading.RLock()
        self.sessions = {}
        self.owner = None
        self.intent = None
        self.ready = False
        self.enabled = enabled
        self.last_output = None
        self.wake = threading.Event()
        self.closed = threading.Event()

    def session(self):
        with self.lock:
            now = self.clock()
            if self.owner and not self.intent and now >= self.sessions[self.owner].get('expires', 0):
                self._stop()
            self.sessions = {k: v for k, v in self.sessions.items()
                             if now - v['seen'] < 3600 or k == self.owner}
            if len(self.sessions) >= 128:
                raise MotionError(503, 'Too many control sessions; close unused control pages.')
            sid = secrets.token_urlsafe(24)
            self.sessions[sid] = {'sequence': 0, 'seen': now, 'token': None}
            return {'session': sid, 'maxSpeed': self.MAX_SPEED,
                    'enabled': self.enabled, 'ready': self.ready,
                    'watchdogMs': self.WATCHDOG_MS, 'leaseMs': int(self.LEASE_SECONDS * 1000)}

    def _stop(self):
        self.intent = None
        self.owner = None
        for session in self.sessions.values():
            session['token'] = None
        self.wake.set()

    def request(self, action, data):
        with self.lock:
            sid, seq = data.get('session'), data.get('sequence')
            session = self.sessions.get(sid) if isinstance(sid, str) else None
            valid_seq = type(seq) is int and 0 < seq < 2**53
            if action == 'stop':
                # Stop always wins, including a stop that arrives before prepare.
                if session and valid_seq:
                    session['sequence'] = max(seq, session['sequence'])
                    session['seen'] = self.clock()
                self._stop()
                return {'stopped': True}
            if action not in ('prepare', 'drive') or not session or not valid_seq:
                raise MotionError(400, 'Invalid control session. Reload the controls.')
            if seq <= session['sequence']:
                raise MotionError(409, 'Stale command rejected.')
            session['sequence'], session['seen'] = seq, self.clock()
            if not self.enabled:
                self._stop()
                raise MotionError(503, 'Driving paused for safety checks.')
            if not self.ready:
                self._stop()
                raise MotionError(503, 'Controller safety stop is not ready.')
            now = self.clock()
            if self.intent and now >= self.intent['until']:
                self._stop()
            if action == 'prepare':
                if self.owner and self.owner != sid:
                    raise MotionError(409, 'Another control page is driving. Release its controls first.')
                self._stop()
                self.owner = sid
            else:
                token = data.get('token')
                if self.owner != sid or not session['token'] or not isinstance(token, str) or not secrets.compare_digest(token, session['token']) or now >= session['expires']:
                    if self.owner == sid:
                        self._stop()
                    raise MotionError(409, 'Motion lease expired. Release and press again.')
                speeds = (data.get('L'), data.get('R'))
                if any(type(v) not in (int, float) or not math.isfinite(v) or abs(v) > self.MAX_SPEED for v in speeds):
                    self._stop()
                    raise MotionError(400, 'Wheel speed exceeds the remote-control limit.')
                # Expiry is fixed when the token is issued, not when a delayed
                # drive packet arrives. A queued packet cannot extend its age.
                self.intent = {'L': speeds[0], 'R': speeds[1], 'until': session['expires']}
            session['token'] = secrets.token_urlsafe(24)
            session['expires'] = now + self.LEASE_SECONDS
            self.wake.set()
            return {'token': session['token'], 'leaseMs': int(self.LEASE_SECONDS * 1000)}

    def tick(self):
        # This worker is the sole sender of wheel commands. A stop cannot be
        # overtaken by a second HTTP request thread sending an older command.
        with self.lock:
            if self.owner and not self.intent and self.clock() >= self.sessions[self.owner].get('expires', 0):
                self._stop()
            if self.intent and self.clock() >= self.intent['until']:
                self._stop()
            command = {'T': 1, 'L': 0, 'R': 0}
            if self.ready and self.intent:
                command.update(L=self.intent['L'], R=self.intent['R'])
            needed = command != self.last_output or self.intent is not None
        if needed:
            try:
                self.send(command)
                self.last_output = command
            except Exception:
                with self.lock:
                    self.ready = False
                    self.last_output = None
                    self._stop()

    def run(self):
        while not self.closed.is_set():
            if not self.ready:
                try:
                    # Both are runtime commands; no firmware or boot mission edits.
                    self.send({'T': 1, 'L': 0, 'R': 0})
                    self.send({'T': 136, 'cmd': self.WATCHDOG_MS})
                    self.last_output = {'T': 1, 'L': 0, 'R': 0}
                    self.ready = True
                except Exception:
                    self.closed.wait(2)
                    continue
            self.tick()
            self.wake.wait(0.1)
            self.wake.clear()

    def start(self):
        threading.Thread(target=self.run, name='rover-motion-stop', daemon=True).start()
