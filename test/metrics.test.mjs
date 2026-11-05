import test from 'node:test';
import assert from 'node:assert/strict';
import { validateEvent,eventKey,summarize } from '../lib/metrics.mjs';
const uuid='c9258ab4-7498-44ca-b6dd-b359aeb0f82e';
const hex='a'.repeat(24),hex2='b'.repeat(24),rh='c'.repeat(24);
test('only allowlisted fields and valid ids',()=>{
  assert.equal(validateEvent({event:'visit',sid:uuid,eid:uuid}).event,'visit');
  assert.equal(validateEvent({event:'visit',sid:uuid,eid:uuid,prompt:'secret'}),null);
  assert.equal(validateEvent({event:'evil',sid:uuid,eid:uuid}),null);
  assert.equal(validateEvent({event:'visit',sid:'id',eid:uuid}),null);
});
test('visit is idempotent per session',()=>{
  const k1=eventKey('2026-11-05','visit',hex,null,hex);
  const k2=eventKey('2026-11-05','visit',hex,null,hex2);
  assert.equal(k1,k2);
});
test('daily sessions, active usage and opted-in revisits',()=>{
  const keys=[
    eventKey('2026-11-04','visit',hex,rh,hex),
    eventKey('2026-11-04','json_created',hex,rh,hex2),
    eventKey('2026-11-05','visit',hex2,rh,hex2),
    eventKey('2026-11-05','json_saved',hex2,rh,hex),
    eventKey('2026-11-05','json_saved',hex2,rh,hex),
    eventKey('2025-01-01','visit',hex,null,hex)
  ];
  const r=summarize(keys,'2026-11-06');
  assert.equal(r.daily.length,2);
  assert.equal(r.daily[0].activeSessions,1);
  assert.equal(r.daily[1].returningOptIn,1);
  assert.equal(r.daily[1].events.json_saved,1);
  assert.equal(r.daily[0].createdSessions,1);
  assert.equal(r.daily[1].savedSessions,1);
  assert.equal(r.weekly.length,1);
  assert.equal(r.monthly.length,1);
});
