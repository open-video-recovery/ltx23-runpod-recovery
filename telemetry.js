// Same-origin-only, best-effort statistics. Never send images, JSON, prompt or credentials.
(() => {
  'use strict';
  const HOST_OK = location.origin === 'https://friendly-elf-6cfdcf.netlify.app';
  const SKEY='ovr-metrics-session-v1';
  const RKEY='ovr-metrics-return-v1';
  const DAYS=30*24*60*60*1000;
  const allowed = new Set([
    'visit','json_created','json_copied','json_saved','endpoint_created',
    'video_started','video_succeeded','video_failed','video_downloaded'
  ]);
  let session;
  try { session=sessionStorage.getItem(SKEY);
    if (!session) { session=crypto.randomUUID(); sessionStorage.setItem(SKEY,session); }
  } catch { session=crypto.randomUUID(); }
  function returningId() {
    try {
      const raw=localStorage.getItem(RKEY);
      if(!raw) return null;
      const obj=JSON.parse(raw);
      if(!obj || !obj.id || obj.expires < Date.now()) {
        localStorage.removeItem(RKEY);return null;
      }
      return obj.id;
    } catch {return null;}
  }
  function track(event) {
    if (!HOST_OK || !allowed.has(event)) return;
    const body={event,sid:session,eid:crypto.randomUUID()};
    const rid=returningId(); if(rid) body.rid=rid;
    try {
      fetch('/.netlify/functions/track', {
        method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify(body),credentials:'omit',cache:'no-store',keepalive:true
      }).catch(()=>{});
    } catch { /* functionality does not depend on telemetry */ }
  }
  window.ovrMetrics=Object.freeze({send:track});
  function init() {
    const check=document.getElementById('metrics-optin');
    if(check) {
      check.checked=Boolean(returningId());
      check.addEventListener('change',()=>{
        try {
          if(check.checked) localStorage.setItem(RKEY,JSON.stringify({
            id:crypto.randomUUID(),expires:Date.now()+DAYS
          }));
          else localStorage.removeItem(RKEY);
        } catch { check.checked=false; }
      });
    }
    // Each open tab is a pseudonymous session; count the visit at most once/day/tab.
    const day=new Date(Date.now()+9*3600000).toISOString().slice(0,10);
    const sentKey=SKEY+'-visit-'+day;
    let wasSent=false;
    try {wasSent=sessionStorage.getItem(sentKey)==='1';} catch {}
    if(!wasSent) {
      track('visit');
      try{sessionStorage.setItem(sentKey,'1');}catch{}
    }
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();
