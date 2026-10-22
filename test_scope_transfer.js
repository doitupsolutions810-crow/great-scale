'use strict';
const assert = require('node:assert/strict');

// Finite reference model only. These checks exercise policy behavior, not theorem proving.
function compose(f, g) {
  if (f.target !== g.source) throw new TypeError('scope type mismatch');
  if (f.preservation !== 'checked' || g.preservation !== 'checked') {
    throw new TypeError('preservation obligation not checked');
  }
  return { source: f.source, target: g.target, preservation: 'checked', map: x => g.map(f.map(x)) };
}
function subset(a, b) { return [...a].every(x => b.has(x)); }
function transferScope(certificate, registry) {
  const record = registry[certificate.id];
  if (!record || record.status !== 'verified') throw new TypeError('transfer certificate not verified');
  if (record.source !== certificate.source || record.target !== certificate.target || record.rule !== certificate.rule) {
    throw new TypeError('certificate binding mismatch');
  }
  return true;
}
function convert(value, from, to, registry) {
  const rule = registry[`${from}->${to}`];
  if (!rule) throw new TypeError('unregistered conversion');
  if (rule.fromDimension !== rule.toDimension) throw new TypeError('dimension mismatch');
  if (rule.status !== 'checked') throw new TypeError('conversion not checked');
  return value * rule.factor;
}
const tests = [];
function test(name, fn) { try { fn(); tests.push({name, ok:true}); } catch(e) { tests.push({name, ok:false, error:e.message}); } }

test('universal claim cannot widen from S to larger T', () => {
  const S=[1,2], T=[1,2,3], P=x=>x!==3;
  assert.equal(S.every(P), true); assert.equal(T.every(P), false);
});
test('universal claim may restrict to a subset', () => {
  const S=[1,2,3], T=[1,2], P=x=>x>0;
  assert.equal(S.every(P), true); assert.equal(T.every(P), true);
});
test('existential witness survives widening', () => {
  const S=[1,2], T=[1,2,3]; assert.ok(S.some(x=>x===2)); assert.ok(T.includes(2));
});
test('existential truth on larger scope does not imply smaller scope', () => {
  const S=[1,2], T=[1,2,3]; assert.ok(T.includes(3)); assert.ok(!S.includes(3));
});
test('compatible morphisms compose', () => {
  const f={source:'S',target:'U',preservation:'checked',map:x=>x+1};
  const g={source:'U',target:'V',preservation:'checked',map:x=>x*2};
  const h=compose(f,g); assert.equal(h.source,'S'); assert.equal(h.target,'V'); assert.equal(h.map(2),6);
});
test('mismatched morphism endpoints reject', () => {
  assert.throws(()=>compose({source:'S',target:'U',preservation:'checked',map:x=>x},{source:'T',target:'V',preservation:'checked',map:x=>x}),/scope type mismatch/);
});
test('unverified preservation obligation rejects', () => {
  assert.throws(()=>compose({source:'S',target:'U',preservation:'checked',map:x=>x},{source:'U',target:'V',preservation:'asserted',map:x=>x}),/not checked/);
});
test('composed map equals sequential application', () => {
  const f={source:'S',target:'U',preservation:'checked',map:x=>x+1};
  const g={source:'U',target:'V',preservation:'checked',map:x=>x*x};
  const h=compose(f,g); for (const x of [0,1,2]) assert.equal(h.map(x),g.map(f.map(x)));
});
test('conclusion scope stays within premise intersection absent transfer', () => {
  const A=new Set(['a','b']), B=new Set(['b','c']), I=new Set([...A].filter(x=>B.has(x)));
  assert.ok(subset(new Set(['b']),I)); assert.ok(!subset(new Set(['b','c']),I));
});
test('registered transfer certificate accepted', () => {
  const registry={'cert-1':{source:'S',target:'T',rule:'embedding',status:'verified'}};
  assert.equal(transferScope({id:'cert-1',source:'S',target:'T',rule:'embedding'},registry),true);
});
test('fabricated transfer certificate rejected', () => {
  assert.throws(()=>transferScope({id:'fake',source:'S',target:'T',rule:'embedding'},{}),/not verified/);
});
test('certificate bound to different target rejected', () => {
  const registry={'cert-1':{source:'S',target:'T',rule:'embedding',status:'verified'}};
  assert.throws(()=>transferScope({id:'cert-1',source:'S',target:'W',rule:'embedding'},registry),/binding mismatch/);
});
test('1 metre converts to 100 centimetres through checked rule', () => {
  const registry={'m->cm':{factor:100,fromDimension:'length',toDimension:'length',status:'checked'}};
  assert.equal(convert(1,'m','cm',registry),100);
});
test('length-to-time conversion rejected by dimensional typing', () => {
  const registry={'m->s':{factor:1,fromDimension:'length',toDimension:'time',status:'checked'}};
  assert.throws(()=>convert(1,'m','s',registry),/dimension mismatch/);
});
test('unregistered unit conversion rejected', () => {
  assert.throws(()=>convert(1,'m','cm',{}),/unregistered/);
});
test('self-asserted conversion rejected', () => {
  const registry={'m->cm':{factor:100,fromDimension:'length',toDimension:'length',status:'asserted'}};
  assert.throws(()=>convert(1,'m','cm',registry),/not checked/);
});

for (const t of tests) console.log(`${t.ok?'PASS':'FAIL'} ${t.name}${t.error?` — ${t.error}`:''}`);
console.log(`\\n${tests.filter(t=>t.ok).length}/${tests.length} passed`);
if (tests.some(t=>!t.ok)) process.exitCode=1;
