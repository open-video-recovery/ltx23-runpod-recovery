import { getStore } from '@netlify/blobs';
import { jstDay, dayOffset } from '../../lib/metrics.mjs';
export default async function handler() {
  const cutoff = dayOffset(jstDay(),-89);
  const store = getStore('ovr-anon-metrics-v1');
  const pending = [];
  try {
    for await(const page of store.list({paginate:true})) {
      for(const {key} of page.blobs) {
        const day=key.slice(0,10);
        if(/^\d{4}-\d{2}-\d{2}$/.test(day) && day < cutoff) {
          pending.push(store.delete(key).catch(()=>{}));
          if(pending.length >= 100) await Promise.all(pending.splice(0));
        }
      }
    }
    await Promise.all(pending);
  } catch { /* no identifiers or request contents are ever logged */ }
}
export const config = {schedule:'0 3 * * *'};
