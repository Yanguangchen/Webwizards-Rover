/* Remote driving uses short server-issued leases; it never queues raw speeds. */
(() => {
  const key = KEY_VALUE, config = CONFIG_VALUE;
  let session = null, sequence = 0, generation = 0, held = false;
  let timer = null, requested = [0, 0];
  const keys = new Set();
  const status = document.getElementById('rover-motion-status');
  const connection = document.getElementById('connection');
  const speed = document.getElementById('speed');
  const maxRate = config.maxSpeed / config.fullSpeed;
  const buttons = document.querySelectorAll('button[data-left]');
  const note = text => { status.textContent = text; };
  const connected = (state, text) => {
    connection.dataset.state = state; connection.textContent = text;
  };
  const api = async (action, body, keepalive = false) => {
    const response = await fetch('/motion/' + action, {
      method: 'POST', headers: {'Content-Type':'application/json', 'X-Rover-Key':key},
      body: JSON.stringify(body), cache: 'no-store', keepalive,
      signal: keepalive ? undefined : AbortSignal.timeout(800)
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Controls unavailable');
    return result;
  };
  function stop(message = 'Stopped — hold a direction to drive.') {
    generation++; held = false; keys.clear(); clearTimeout(timer);
    note(message);
    api('stop', {session, sequence: ++sequence}, true).catch(() => {
      connected('offline', 'Signal lost');
      note('Signal lost — automatic stop is active. Release and press again when connected.');
    });
  }
  async function renew(token, current) {
    if (!held || current !== generation) return;
    try {
      const result = await api('drive', {session, sequence: ++sequence, token,
        L: requested[0], R: requested[1]});
      if (!held || current !== generation) return;
      connected('online', 'Connected');
      note('Driving — release to stop.');
      timer = setTimeout(() => renew(result.token, current), 75);
    } catch (error) {
      if (current === generation) stop('Stopped — ' + error.message + ' Release and press again.');
    }
  }
  async function drive(left, right) {
    if (!left && !right) { stop(); return; }
    if (!session) { note('Controls are still connecting.'); return; }
    clearTimeout(timer);
    const current = ++generation;
    held = true;
    const candidate = Number(window.speed_rate);
    const rate = Math.max(0.1, Math.min(Number.isFinite(candidate) ? candidate : config.defaultRate, maxRate));
    requested = [left, right].map(value => Math.max(-config.maxSpeed, Math.min(config.maxSpeed, value * rate)));
    try {
      const result = await api('prepare', {session, sequence: ++sequence});
      if (held && current === generation) await renew(result.token, current);
    } catch (error) {
      if (current === generation) stop('Stopped — ' + error.message);
    }
  }
  window.speed_rate = config.defaultRate;
  window.movtionButton = drive;
  speed.max = String(Math.round(maxRate * 100));
  speed.value = String(Math.round(config.defaultRate * 100));
  document.getElementById('speed-limit').textContent = speed.max + '% · Maximum';
  function updateSpeed() {
    if (held) stop('Stopped — speed changed. Hold a direction to continue.');
    window.speed_rate = Math.max(0.1, Math.min(Number(speed.value) / 100, maxRate));
    document.getElementById('speed-value').textContent = Math.round(window.speed_rate * 100) + '%';
  }
  speed.addEventListener('input', updateSpeed);
  updateSpeed();
  for (const button of buttons) {
    button.addEventListener('pointerdown', event => {
      if (event.button !== 0 || event.isPrimary === false) return;
      event.preventDefault(); keys.clear(); button.setPointerCapture(event.pointerId);
      drive(Number(button.dataset.left), Number(button.dataset.right));
    });
    for (const type of ['pointerup','pointercancel','lostpointercapture','pointerleave']) {
      button.addEventListener(type, () => { if (held) stop(); });
    }
    button.addEventListener('contextmenu', event => event.preventDefault());
  }
  document.getElementById('stop').addEventListener('pointerdown', event => { event.preventDefault(); stop(); });
  document.getElementById('stop').addEventListener('click', () => stop());
  const directions = new Set(['w','a','s','d','ArrowUp','ArrowDown','ArrowLeft','ArrowRight']);
  function keyboardDrive() {
    const forward = Number(keys.has('w') || keys.has('ArrowUp')) - Number(keys.has('s') || keys.has('ArrowDown'));
    const turn = Number(keys.has('d') || keys.has('ArrowRight')) - Number(keys.has('a') || keys.has('ArrowLeft'));
    drive(Math.max(-0.5, Math.min(0.5, 0.5 * (forward + turn))),
      Math.max(-0.5, Math.min(0.5, 0.5 * (forward - turn))));
  }
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' || (event.key === ' ' && !/INPUT|TEXTAREA|SELECT/.test(event.target.tagName))) {
      event.preventDefault(); stop(); return;
    }
    if (!directions.has(event.key) || event.repeat || /INPUT|TEXTAREA|SELECT/.test(event.target.tagName)) return;
    event.preventDefault(); keys.add(event.key); keyboardDrive();
  });
  document.addEventListener('keyup', event => {
    if (!directions.has(event.key) || !keys.has(event.key)) return;
    event.preventDefault(); keys.delete(event.key); keyboardDrive();
  });
  const release = () => { keys.clear(); if (held) stop(); };
  window.addEventListener('blur', release);
  window.addEventListener('pagehide', release);
  document.addEventListener('visibilitychange', () => { if (document.hidden) release(); });
  document.addEventListener('pointerup', release);
  document.addEventListener('pointercancel', release);
  async function telemetry() {
    if (!document.hidden) {
      try {
        const response = await fetch('/origin/js?' + new URLSearchParams({json:JSON.stringify({T:130})}), {
          headers:{'X-Rover-Key':key}, cache:'no-store', signal:AbortSignal.timeout(2500)
        });
        if (!response.ok) throw new Error('Controller unavailable');
        const data = await response.json();
        const voltage = Number(data.v);
        document.getElementById('battery').textContent = Number.isFinite(voltage) && voltage > 0 ? voltage.toFixed(1) + ' V' : '—';
        connected('online', 'Connected');
      } catch {
        document.getElementById('battery').textContent = '—';
        if (!held) connected('offline', 'Signal lost');
      }
    }
    setTimeout(telemetry, 3000);
  }
  api('session', {}).then(result => {
    session = result.session;
    for (const button of buttons) button.disabled = !result.enabled;
    note(result.enabled ? 'Stopped — hold a direction to drive.' : 'Driving is unavailable.');
    telemetry();
  }).catch(() => {
    connected('offline', 'Offline');
    note('Controls unavailable. Reload when the rover is connected.');
  });
})();
