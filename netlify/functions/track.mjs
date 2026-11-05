import { createHmac } from 'node:crypto';
import { getStore } from '@netlify/blobs';
import { eventKey, jstDay, validateEvent } from '../../lib/metrics.mjs';
const reply = (status) => new Response(null,{status,headers:{
  'Cache-Control':'no-store', 'Access-Control-Allow-Origin':'null'
}});
export default async function handler(request) {
  if (request.method !== 'POST') return reply(405);
  // Fail closed until a long, private Netlify environment secret is installed.
  const secret = process.env.ANALYTICS_ADMIN_TOKEN;
  if (!secret || secret.length < 32) return reply(204);
  if (process.env.CONTEXT && process.env.CONTEXT !== 'production') return reply(204);
  if (request.headers.get('origin') !== new URL(request.url).origin) return reply(403);
  if (!(request.headers.get('content-type') || '').startsWith('application/json')) return reply(415);
  const length = Number(request.headers.get('content-length') || 0);
  if (length > 320) return reply(413);
  let payload;
  try {
    const raw = await request.text();
    if (raw.length > 320) return reply(413);
    payload = validateEvent(JSON.parse(raw));
  } catch { return reply(400); }
  if (!payload) return reply(400);
  // HMAC avoids saving client-provided pseudonyms verbatim.
  const digest = value => createHmac('sha256',secret).update('ovr-metrics-v1:' + value).digest('hex').slice(0,24);
  const key = eventKey(jstDay(),payload.event,digest(payload.sid),
    payload.rid ? digest('return:'+payload.rid) : null,digest(payload.eid));
  try {
    await getStore({name:'ovr-anon-metrics-v1',consistency:'strong'}).set(key,'',{onlyIfNew:true});
    return reply(204);
  } catch {
    // Telemetry is best-effort. Never log incoming requests or their identifiers.
    return reply(204);
  }
}
export const config = { rateLimit: {
  action:'rate_limit', aggregateBy:'ip', windowSize:60, windowLimit:45
}};
