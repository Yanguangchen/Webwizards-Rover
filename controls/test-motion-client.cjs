const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const {test} = require('node:test');
const flush = () => new Promise(resolve => setImmediate(resolve));
async function setup() {
  const requests=[], timers=new Map(); let next=0;
  const target = () => ({listeners:{},style:{},dataset:{},disabled:true,addEventListener(k,f){this.listeners[k]=f;},setAttribute(){},removeAttribute(){}});
  const button=target(); button.dataset={left:'.5',right:'.5'}; button.setPointerCapture=()=>{};
  const elements=Object.fromEntries(['rover-motion-status','connection','speed','speed-limit','speed-value','battery','stop'].map(id=>[id,target()]));
  const document=target(); document.body={prepend(){}}; document.createElement=target; document.querySelectorAll=()=>[button]; document.getElementById=id=>elements[id];
  const window=target(); window.document=document;
  const context={window,document,KEY_VALUE:'test-key',CONFIG_VALUE:{maxSpeed:.25,fullSpeed:.5,defaultRate:.3},AbortSignal,URLSearchParams,
    setTimeout(f,delay){const id=++next;if(delay!==3000)timers.set(id,f);return id;},clearTimeout(id){timers.delete(id);},
    fetch(url,options){if(url.startsWith('/origin/js?')) return Promise.resolve({ok:true,json:async()=>({v:11.8})}); const body=JSON.parse(options.body);return new Promise(resolve=>{
      const entry={url,body,resolve:data=>resolve({ok:true,json:async()=>data})}; requests.push(entry);
      if(url.endsWith('/session'))entry.resolve({session:'test-session',enabled:true});
      if(url.endsWith('/stop'))entry.resolve({stopped:true});
    });}
  };
  vm.runInNewContext(fs.readFileSync(require('node:path').join(__dirname,'motion-client.js'),'utf8'),context);
  await flush(); return {requests,timers,window,document,button,elements};
}
test('quick release before prepare returns never sends movement',async()=>{
  const c=await setup(); c.window.movtionButton(.5,.5); c.window.movtionButton(0,0);
  const prep=c.requests.find(r=>r.url.endsWith('/prepare')); prep.resolve({token:'late-token'}); await flush();
  assert.equal(c.requests.filter(r=>r.url.endsWith('/drive')).length,0);
  assert(c.requests.find(r=>r.url.endsWith('/stop')).body.sequence>prep.body.sequence);
});
test('late drive response after release cannot schedule a renewal',async()=>{
  const c=await setup(); c.window.movtionButton(.5,.5);
  c.requests.find(r=>r.url.endsWith('/prepare')).resolve({token:'first'}); await flush();
  const drive=c.requests.find(r=>r.url.endsWith('/drive')); assert.equal(drive.body.L,.15);
  c.window.movtionButton(0,0); drive.resolve({token:'late-renewal'}); await flush(); assert.equal(c.timers.size,0);
});
test('pointer cancellation and lost window focus send stops',async()=>{
  for(const event of ['pointercancel','blur']) {
    const c=await setup(); c.button.listeners.pointerdown({button:0,pointerId:1,preventDefault(){}});
    (event==='blur'?c.window:c.button).listeners[event]();
    assert.equal(c.requests.filter(r=>r.url.endsWith('/stop')).length,1);
  }
});
test('fast preset cannot exceed remote speed cap',async()=>{
  const c=await setup(); c.window.speed_rate=1; c.window.movtionButton(.5,.5);
  c.requests.find(r=>r.url.endsWith('/prepare')).resolve({token:'first'}); await flush();
  assert.equal(c.requests.find(r=>r.url.endsWith('/drive')).body.L,.25);
});

test('speed change during a hold stops and requires a fresh press',async()=>{
  const c=await setup(); c.window.movtionButton(.5,.5);
  c.elements.speed.value='45'; c.elements.speed.listeners.input();
  c.requests.find(r=>r.url.endsWith('/prepare')).resolve({token:'late'}); await flush();
  assert.equal(c.requests.filter(r=>r.url.endsWith('/drive')).length,0);
  assert.equal(c.requests.filter(r=>r.url.endsWith('/stop')).length,1);
  assert.equal(c.elements['speed-value'].textContent,'45%');
  c.window.movtionButton(.5,.5);
  c.requests.filter(r=>r.url.endsWith('/prepare')).at(-1).resolve({token:'fresh'}); await flush();
  assert.equal(c.requests.find(r=>r.url.endsWith('/drive')).body.L,.225);
});
test('space, Escape, and page hiding stop held movement',async()=>{
  for(const event of [' ','Escape','hidden']) {
    const c=await setup(); c.window.movtionButton(.5,.5);
    if(event==='hidden'){c.document.hidden=true;c.document.listeners.visibilitychange();}
    else c.document.listeners.keydown({key:event,target:{tagName:'BODY'},preventDefault(){}});
    c.requests.find(r=>r.url.endsWith('/prepare')).resolve({token:'late'}); await flush();
    assert.equal(c.requests.filter(r=>r.url.endsWith('/stop')).length,1);
    assert.equal(c.requests.filter(r=>r.url.endsWith('/drive')).length,0);
  }
});
test('telemetry is displayed without issuing motion',async()=>{
  const c=await setup();
  assert.equal(c.elements.battery.textContent,'11.8 V');
  assert.equal(c.elements.connection.textContent,'Connected');
  assert.equal(c.button.disabled,false);
  assert.equal(c.requests.filter(r=>r.url.endsWith('/drive')||r.url.endsWith('/prepare')).length,0);
});
