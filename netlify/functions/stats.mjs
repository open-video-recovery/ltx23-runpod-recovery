import { timingSafeEqual } from 'node:crypto';
import { getStore } from '@netlify/blobs';
import { jstDay, summarize } from '../../lib/metrics.mjs';
const json = (value,status=200) => new Response(JSON.stringify(value),{
  status,headers:{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store',
  'X-Content-Type-Options':'nosniff'}
});
export default async function handler(request) {
  if(request.method !== 'GET') return json({error:'Method not allowed'},405);
  const expected=process.env.ANALYTICS_ADMIN_TOKEN || '';
  if(expected.length < 32) return json({error:'Admin secret is not configured'},503);
  const given=(request.headers.get('authorization') || '').replace(/^Bearer /,'');
  const a=Buffer.from(expected), b=Buffer.from(given);
  if(a.length!==b.length || !timingSafeEqual(a,b)) return json({error:'Unauthorized'},401);
  const days=Number(new URL(request.url).searchParams.get('days') || 90);
  if(!Number.isInteger(days)|| days<1 || days>90) return json({error:'Invalid days'},400);
  try {
    const keys=[];
    for await (const page of getStore('ovr-anon-metrics-v1').list({paginate:true})) {
      for (const item of page.blobs) keys.push(item.key);
      if(keys.length > 500000) return json({error:'Too many records; aggregate offline'},503);
    }
    return json(summarize(keys,jstDay(),days));
  } catch {
    return json({error:'Statistics storage is unavailable'},503);
  }
}
