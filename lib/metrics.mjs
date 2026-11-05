// Shared, deliberately narrow analytics schema. No payloads, prompts or RunPod identifiers.
export const EVENTS = Object.freeze([
  'visit', 'json_created', 'json_copied', 'json_saved',
  'endpoint_created', 'video_started', 'video_succeeded',
  'video_failed', 'video_downloaded'
]);
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
export const jstDay = (date = new Date()) =>
  new Date(date.getTime() + 9 * 3600000).toISOString().slice(0, 10);
export const dayOffset = (day, offset) => {
  const d = new Date(day + 'T00:00:00Z');
  d.setUTCDate(d.getUTCDate() + offset);
  return d.toISOString().slice(0, 10);
};
export function validateEvent(body) {
  if (!body || typeof body !== 'object' || Array.isArray(body)) return null;
  const fields = Object.keys(body);
  if (fields.some(k => !['event','sid','eid','rid'].includes(k))) return null;
  if (!EVENTS.includes(body.event) || !UUID.test(body.sid || '') ||
      !UUID.test(body.eid || '') || (body.rid !== undefined && !UUID.test(body.rid))) return null;
  return { event: body.event, sid: body.sid, eid: body.eid, rid: body.rid || null };
}
// Keys only: day/event/HMAC(session)/HMAC(opt-in returning ID) or '-'/HMAC(event ID).
// Visit uses the session ID for idempotence. No client data is stored as Blob contents.
export function eventKey(day, event, sessionHash, returningHash, eventHash) {
  return [day, event, sessionHash, returningHash || '-', event === 'visit' ? sessionHash : eventHash].join('/');
}
export function summarize(keys, today = jstDay(), days = 90) {
  const oldest = dayOffset(today, -(days - 1));
  const daily = new Map();
  const seen = new Set();
  for (const key of keys) {
    const [day, ev, sid, rid, eid, ...extra] = key.split('/');
    if (extra.length || !/^\d{4}-\d{2}-\d{2}$/.test(day || '') ||
        day < oldest || day > today || !EVENTS.includes(ev) ||
        !/^[0-9a-f]{24}$/.test(sid || '') ||
        !(rid === '-' || /^[0-9a-f]{24}$/.test(rid || '')) ||
        !/^[0-9a-f]{24}$/.test(eid || '') || seen.has(key)) continue;
    seen.add(key);
    if (!daily.has(day)) daily.set(day, {
      day, sessions: new Set(), active: new Set(), returningIds: new Set(),
      events: Object.fromEntries(EVENTS.map(x=>[x,0]))
    });
    const x = daily.get(day);
    x.events[ev]++;
    x.sessions.add(sid);
    if (ev !== 'visit') x.active.add(sid);
    if (ev === 'visit' && rid !== '-') x.returningIds.add(rid);
  }
  const seenReturning = new Set();
  const rows = [...daily.values()].sort((a,b)=>a.day.localeCompare(b.day)).map(x=>{
    let repeatOptIn = 0;
    for (const id of x.returningIds) {
      if (seenReturning.has(id)) repeatOptIn++;
      seenReturning.add(id);
    }
    return {
      day:x.day, sessions:x.sessions.size, activeSessions:x.active.size,
      optInVisitors:x.returningIds.size, returningOptIn:repeatOptIn, events:x.events
    };
  });
  const months = new Map();
  for (const row of rows) {
    const month = row.day.slice(0,7);
    if(!months.has(month)) months.set(month,{
      month,sessions:0,activeSessions:0,returningOptIn:0,
      events:Object.fromEntries(EVENTS.map(x=>[x,0]))
    });
    const m=months.get(month);
    m.sessions+=row.sessions; m.activeSessions+=row.activeSessions;
    m.returningOptIn+=row.returningOptIn;
    for (const ev of EVENTS) m.events[ev]+=row.events[ev];
  }
  return { timezone:'Asia/Tokyo', retentionDays:90, daily:rows,
    monthly:[...months.values()], definition:'Sessions are per-tab anonymous sessions, not distinct people. Returning counts include only optional 30-day pseudonymous opt-ins and are limited to the visible retention window.' };
}
