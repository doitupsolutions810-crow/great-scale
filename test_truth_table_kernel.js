'use strict';
const assert = require('node:assert/strict');

// Exhaustive finite propositional-entailment checker.
// AST: {op:'var', name}, {op:'not', arg}, {op:'and'|'or'|'imp', left, right}
// This checks truth-table entailment over the variables actually present.
// It is not a proof assistant for higher-order logic, arithmetic, or quantum physics.

function validate(ast) {
  if (!ast || typeof ast !== 'object' || Array.isArray(ast)) throw new TypeError('malformed formula');
  if (ast.op === 'var') {
    if (typeof ast.name !== 'string' || !/^[A-Za-z][A-Za-z0-9_]*$/.test(ast.name)) throw new TypeError('invalid variable');
    return;
  }
  if (ast.op === 'not') return validate(ast.arg);
  if (['and', 'or', 'imp'].includes(ast.op)) {
    validate(ast.left); validate(ast.right); return;
  }
  throw new TypeError('unknown operator');
}
function vars(ast, out = new Set()) {
  if (ast.op === 'var') out.add(ast.name);
  else if (ast.op === 'not') vars(ast.arg, out);
  else { vars(ast.left, out); vars(ast.right, out); }
  return out;
}
function evaluate(ast, valuation) {
  if (ast.op === 'var') return valuation[ast.name];
  if (ast.op === 'not') return !evaluate(ast.arg, valuation);
  const l = evaluate(ast.left, valuation), r = evaluate(ast.right, valuation);
  if (ast.op === 'and') return l && r;
  if (ast.op === 'or') return l || r;
  if (ast.op === 'imp') return !l || r;
  throw new TypeError('unknown operator');
}
function checkEntailment(claim) {
  if (!claim || !Array.isArray(claim.assumptions) || !claim.conclusion) throw new TypeError('malformed claim');
  claim.assumptions.forEach(validate); validate(claim.conclusion);
  const names = [...new Set([...claim.assumptions.flatMap(a => [...vars(a)]), ...vars(claim.conclusion)])].sort();
  if (names.length > 16) throw new RangeError('too many variables for exhaustive checker');
  const rows = 2 ** names.length;
  for (let mask = 0; mask < rows; mask++) {
    const valuation = Object.fromEntries(names.map((name, i) => [name, Boolean(mask & (1 << i))]));
    if (claim.assumptions.every(a => evaluate(a, valuation)) && !evaluate(claim.conclusion, valuation)) {
      return { accepted: false, counterexample: valuation, checkedRows: rows };
    }
  }
  return { accepted: true, checkedRows: rows };
}
const V = name => ({op:'var',name});
const NOT = arg => ({op:'not',arg});
const AND = (left,right) => ({op:'and',left,right});
const OR = (left,right) => ({op:'or',left,right});
const IMP = (left,right) => ({op:'imp',left,right});
const tests=[];
function test(name, fn) { try { fn(); tests.push({name,ok:true}); } catch(e) { tests.push({name,ok:false,error:e.message}); } }

test('modus ponens entailment accepted', () => {
  assert.equal(checkEntailment({assumptions:[V('P'),IMP(V('P'),V('Q'))],conclusion:V('Q')}).accepted,true);
});
test('conjunction introduction entailment accepted', () => {
  assert.equal(checkEntailment({assumptions:[V('P'),V('Q')],conclusion:AND(V('P'),V('Q'))}).accepted,true);
});
test('excluded middle accepted', () => {
  assert.equal(checkEntailment({assumptions:[],conclusion:OR(V('P'),NOT(V('P')))}).accepted,true);
});
test('contradictory assumptions entail any conclusion by classical semantics', () => {
  assert.equal(checkEntailment({assumptions:[V('P'),NOT(V('P'))],conclusion:V('Q')}).accepted,true);
});
test('invalid inference P does not entail Q rejected with counterexample', () => {
  const r=checkEntailment({assumptions:[V('P')],conclusion:V('Q')});
  assert.equal(r.accepted,false); assert.deepEqual(r.counterexample,{P:true,Q:false});
});
test('assumption tampering changes result', () => {
  assert.equal(checkEntailment({assumptions:[V('P')],conclusion:V('P')}).accepted,true);
  assert.equal(checkEntailment({assumptions:[],conclusion:V('P')}).accepted,false);
});
test('conclusion tampering is checked, not trusted by certificate label', () => {
  assert.equal(checkEntailment({assumptions:[V('P')],conclusion:V('P')}).accepted,true);
  assert.equal(checkEntailment({assumptions:[V('P')],conclusion:V('Q')}).accepted,false);
});
test('unknown operator rejected', () => {
  assert.throws(()=>checkEntailment({assumptions:[],conclusion:{op:'magic'}}),/unknown operator/);
});
test('malformed formula rejected', () => {
  assert.throws(()=>checkEntailment({assumptions:[],conclusion:null}),/malformed claim/);
});
test('invalid variable identifier rejected', () => {
  assert.throws(()=>checkEntailment({assumptions:[],conclusion:V('P;evil')}),/invalid variable/);
});
test('truth-table coverage count is exact for three variables', () => {
  const r=checkEntailment({assumptions:[],conclusion:IMP(AND(V('P'),V('Q')),V('R'))});
  assert.equal(r.checkedRows,8); assert.equal(r.accepted,false);
});
test('tautology passes for all truth assignments', () => {
  const r=checkEntailment({assumptions:[],conclusion:IMP(AND(V('P'),V('Q')),V('P'))});
  assert.equal(r.checkedRows,4); assert.equal(r.accepted,true);
});
test('too many variables fail closed', () => {
  const vars=Array.from({length:17},(_,i)=>V('P'+i));
  assert.throws(()=>checkEntailment({assumptions:[],conclusion:vars.reduce((a,b)=>OR(a,b))}),/too many variables/);
});
test('formula variable ordering does not change entailment', () => {
  const a=checkEntailment({assumptions:[AND(V('P'),V('Q'))],conclusion:V('P')});
  const b=checkEntailment({assumptions:[AND(V('Q'),V('P'))],conclusion:V('P')});
  assert.equal(a.accepted,b.accepted);
});
test('counterexample establishes scope-limited failure', () => {
  const r=checkEntailment({assumptions:[IMP(V('P'),V('Q'))],conclusion:V('P')});
  assert.equal(r.accepted,false);
  assert.equal(evaluate(IMP(V('P'),V('Q')),r.counterexample),true);
  assert.equal(evaluate(V('P'),r.counterexample),false);
});
test('claim type boundary: truth-table checker only handles propositional AST', () => {
  assert.throws(()=>checkEntailment({assumptions:[],conclusion:{op:'forall',body:V('P')}}),/unknown operator/);
});

for (const t of tests) console.log(`${t.ok?'PASS':'FAIL'} ${t.name}${t.error?` — ${t.error}`:''}`);
console.log(`\n${tests.filter(t=>t.ok).length}/${tests.length} passed`);
if (tests.some(t=>!t.ok)) process.exitCode=1;
