'use strict';
const assert = require('node:assert/strict');

// Exhaustive finite propositional-entailment checker.
// AST: {op:'var', name}, {op:'not', arg}, {op:'and'|'or'|'imp', left, right}
// This checks truth-table entailment over the variables actually present.
// It is not a proof assistant for higher-order logic, arithmetic, or quantum physics.

const MAX_DEPTH = 256;
const MAX_NODES = 10000;
const MAX_VARIABLES = 16;
const MAX_EVAL_STEPS = 2000000;

function validate(ast, budget={nodes:0}, depth=0) {
  if (depth > MAX_DEPTH) throw new RangeError('formula depth limit exceeded');
  if (++budget.nodes > MAX_NODES) throw new RangeError('claim AST node limit exceeded');
  if (!ast || typeof ast !== 'object' || Array.isArray(ast) || Object.getPrototypeOf(ast)!==Object.prototype) throw new TypeError('malformed formula');
  const keys=Reflect.ownKeys(ast);
  if (keys.some(k=>typeof k!=='string')) throw new TypeError('malformed formula schema');
  for (const key of keys) {
    const descriptor=Object.getOwnPropertyDescriptor(ast,key);
    if (!descriptor || !Object.prototype.hasOwnProperty.call(descriptor,'value')) throw new TypeError('formula accessors are not allowed');
  }
  const requireKeys=expected=>{
    const actual=[...keys].sort(), wanted=[...expected].sort();
    if (JSON.stringify(actual)!==JSON.stringify(wanted)) throw new TypeError('malformed formula schema');
  };
  if (ast.op === 'var') {
    requireKeys(['op','name']);
    if (typeof ast.name !== 'string' || !/^[A-Za-z][A-Za-z0-9_]*$/.test(ast.name)) throw new TypeError('invalid variable');
    return true;
  }
  if (ast.op === 'not') {
    requireKeys(['op','arg']);
    return validate(ast.arg,budget,depth+1);
  }
  if (['and', 'or', 'imp'].includes(ast.op)) {
    requireKeys(['op','left','right']);
    validate(ast.left,budget,depth+1); validate(ast.right,budget,depth+1); return true;
  }
  throw new TypeError('unknown operator');
}
function vars(ast, out = new Set()) {
  if (ast.op === 'var') out.add(ast.name);
  else if (ast.op === 'not') vars(ast.arg, out);
  else { vars(ast.left, out); vars(ast.right, out); }
  return out;
}
function evaluate(ast, valuation, steps={count:0}) {
  if (++steps.count > MAX_EVAL_STEPS) throw new RangeError('truth-table evaluation work limit exceeded');
  if (ast.op === 'var') {
    if (!valuation || typeof valuation !== 'object' || Array.isArray(valuation)) throw new TypeError('valuation must be an object');
    if (!Object.prototype.hasOwnProperty.call(valuation,ast.name)) throw new TypeError('missing Boolean assignment');
    if (typeof valuation[ast.name] !== 'boolean') throw new TypeError('assignment must be Boolean');
    return valuation[ast.name];
  }
  if (ast.op === 'not') return !evaluate(ast.arg, valuation, steps);
  const l = evaluate(ast.left, valuation, steps), r = evaluate(ast.right, valuation, steps);
  if (ast.op === 'and') return l && r;
  if (ast.op === 'or') return l || r;
  if (ast.op === 'imp') return !l || r;
  throw new TypeError('unknown operator');
}
function checkEntailment(claim) {
  if (!claim || typeof claim!=='object' || Array.isArray(claim) || Object.getPrototypeOf(claim)!==Object.prototype) throw new TypeError('malformed claim');
  const claimKeys=Reflect.ownKeys(claim);
  if (claimKeys.length!==2 || !claimKeys.includes('assumptions') || !claimKeys.includes('conclusion')) throw new TypeError('malformed claim schema');
  for(const key of claimKeys) {
    const descriptor=Object.getOwnPropertyDescriptor(claim,key);
    if (!descriptor || !Object.prototype.hasOwnProperty.call(descriptor,'value')) throw new TypeError('claim accessors are not allowed');
  }
  if (!Array.isArray(claim.assumptions) || Object.getPrototypeOf(claim.assumptions)!==Array.prototype || !claim.conclusion) throw new TypeError('malformed claim');
  if (claim.assumptions.length > MAX_NODES) throw new RangeError('assumption count limit exceeded');
  const assumptionKeys=Reflect.ownKeys(claim.assumptions);
  // The array may contain only its length and dense numeric elements.
  // Reject custom keys before any iteration can consult a custom iterator.
  if (assumptionKeys.length!==claim.assumptions.length+1 || assumptionKeys.some(key=>key!=='length' && (typeof key!=='string' || !/^(0|[1-9][0-9]*)$/.test(key) || Number(key)>=claim.assumptions.length))) throw new TypeError('malformed assumptions array schema');
  for(let i=0;i<claim.assumptions.length;i++) {
    const descriptor=Object.getOwnPropertyDescriptor(claim.assumptions,String(i));
    if (!descriptor) throw new TypeError('sparse assumptions are not allowed');
    if (!Object.prototype.hasOwnProperty.call(descriptor,'value')) throw new TypeError('assumption accessors are not allowed');
  }
  const budget={nodes:0};
  for(const a of claim.assumptions) validate(a,budget);
  validate(claim.conclusion,budget);
  const names = [...new Set([...claim.assumptions.flatMap(a => [...vars(a)]), ...vars(claim.conclusion)])].sort();
  if (names.length > MAX_VARIABLES) throw new RangeError('too many variables for exhaustive checker');
  const rows = 2 ** names.length, steps={count:0};
  for (let mask = 0; mask < rows; mask++) {
    const valuation = Object.fromEntries(names.map((name, i) => [name, Boolean(mask & (1 << i))]));
    if (claim.assumptions.every(a => evaluate(a, valuation,steps)) && !evaluate(claim.conclusion, valuation,steps)) {
      return { accepted: false, counterexample: valuation, checkedRows: rows, evaluationSteps:steps.count };
    }
  }
  return { accepted: true, checkedRows: rows, evaluationSteps:steps.count };
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


test('cyclic AST rejected at the recursion boundary', () => {
  const ast=NOT(V('P'));ast.arg=ast;
  assert.throws(()=>checkEntailment({assumptions:[],conclusion:ast}),/formula depth limit exceeded/);
});
test('aggregate node budget covers assumptions and conclusion together', () => {
  const leaves=Array.from({length:3000},(_,i)=>V('P'+(i%3)));
  function balanced(xs){if(xs.length===1)return xs[0];const m=Math.floor(xs.length/2);return AND(balanced(xs.slice(0,m)),balanced(xs.slice(m)));}
  const big=balanced(leaves);
  assert.throws(()=>checkEntailment({assumptions:[big,big],conclusion:V('P0')}),/claim AST node limit exceeded/);
});
test('truth-table work budget caps repeated formula evaluation', () => {
  const tautologies=Array.from({length:1800},(_,i)=>IMP(V('P'+(i%16)),V('P'+(i%16))));
  assert.throws(()=>checkEntailment({assumptions:tautologies,conclusion:IMP(V('P0'),V('P0'))}),/evaluation work limit exceeded/);
});
test('evaluator rejects inherited and non-Boolean assignments', () => {
  assert.throws(()=>evaluate(V('toString'),{}),/missing Boolean assignment/);
  assert.throws(()=>evaluate(V('P'),{P:'false'}),/assignment must be Boolean/);
  assert.equal(evaluate(V('P'),{P:false}),false);
});


test('formula schema rejects inherited fields and extra keys', () => {
  assert.throws(()=>checkEntailment({assumptions:[],conclusion:Object.assign(V('P'),{extra:true})}),/malformed formula schema/);
  const inherited=Object.create({op:'var',name:'P'});
  assert.throws(()=>checkEntailment({assumptions:[],conclusion:inherited}),/malformed formula/);
});
test('claim rejects sparse assumptions and oversized assumption lists', () => {
  const sparse=[];sparse.length=2;sparse[1]=V('P');
  assert.throws(()=>checkEntailment({assumptions:sparse,conclusion:V('P')}),/malformed assumptions array schema|sparse assumptions/);
  const many=Array.from({length:MAX_NODES+1},()=>V('P'));
  assert.throws(()=>checkEntailment({assumptions:many,conclusion:V('P')}),/assumption count limit/);
});


test('claim schema rejects inherited and accessor-backed fields', () => {
  const inherited=Object.create({assumptions:[],conclusion:V('P')});
  assert.throws(()=>checkEntailment(inherited),/malformed claim/);
  const accessor={};Object.defineProperty(accessor,'assumptions',{enumerable:true,get(){throw Error('getter invoked')}});
  Object.defineProperty(accessor,'conclusion',{enumerable:true,value:V('P')});
  assert.throws(()=>checkEntailment(accessor),/claim accessors are not allowed/);
});


test('assumption arrays reject custom keys and custom prototypes', () => {
  const extra=[V('P')];extra.note='unexpected';
  assert.throws(()=>checkEntailment({assumptions:extra,conclusion:V('P')}),/malformed assumptions array schema/);
  const proto=Object.create(Array.prototype);proto.push=Array.prototype.push;
  const custom=Object.assign(Object.create(proto),[V('P')]);
  custom.length=1;
  assert.throws(()=>checkEntailment({assumptions:custom,conclusion:V('P')}),/malformed claim/);
});

for (const t of tests) console.log(`${t.ok?'PASS':'FAIL'} ${t.name}${t.error?` — ${t.error}`:''}`);
console.log(`\n${tests.filter(t=>t.ok).length}/${tests.length} passed`);
if (tests.some(t=>!t.ok)) process.exitCode=1;
