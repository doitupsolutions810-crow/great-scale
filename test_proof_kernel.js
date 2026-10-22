'use strict';
const assert=require('node:assert/strict');
const {MAX_ATOMS,MAX_EVAL_STEPS,MAX_NODES,MAX_ATOM_LENGTH,MAX_RULE_LENGTH,validateFormula,check,checkBound,tautologyUnderContext,evalF}=require('./proof_kernel');
const A='A',B='B',C='C';
let passed=0,failed=0;const results=[];
function test(name,fn){try{fn();passed++;results.push({name,ok:true})}catch(e){failed++;results.push({name,ok:false,error:e.message})}}
function verify(p){const r=check(p);assert.equal(tautologyUnderContext(r.conclusion,r.context),true,'truth-table oracle rejected derivation');return r}
const assume=x=>({rule:'assume',formula:x});
test('assumption accepted under itself',()=>{const r=verify(assume(A));assert.deepEqual(r.context,[A]);assert.equal(r.conclusion,A)});
test('conjunction introduction sound',()=>{assert.deepEqual(verify({rule:'andI',left:assume(A),right:assume(B)}).conclusion,['and',A,B])});
test('left conjunction elimination sound',()=>{assert.equal(verify({rule:'andEL',proof:{rule:'andI',left:assume(A),right:assume(B)}}).conclusion,A)});
test('right conjunction elimination sound',()=>{assert.equal(verify({rule:'andER',proof:{rule:'andI',left:assume(A),right:assume(B)}}).conclusion,B)});
test('implication introduction discharges assumption',()=>{const r=verify({rule:'impI',assumption:A,proof:assume(A)});assert.deepEqual(r.conclusion,['imp',A,A]);assert.deepEqual(r.context,[])});
test('modus ponens sound',()=>{const r=verify({rule:'impE',function:assume(['imp',A,B]),argument:assume(A)});assert.equal(r.conclusion,B);assert.equal(tautologyUnderContext(B,[['imp',A,B],A]),true)});
test('both disjunction introductions sound',()=>{assert.deepEqual(verify({rule:'orIL',proof:assume(A),other:B}).conclusion,['or',A,B]);assert.deepEqual(verify({rule:'orIR',proof:assume(B),other:A}).conclusion,['or',A,B])});
test('unknown inference rule rejected',()=>{assert.throws(()=>check({rule:'magic',formula:A}),/unknown inference rule/)});
test('conjunction elimination on atom rejected',()=>{assert.throws(()=>check({rule:'andEL',proof:assume(A)}),/requires conjunction/)});
test('wrong modus ponens antecedent rejected',()=>{assert.throws(()=>check({rule:'impE',function:assume(['imp',A,B]),argument:assume(C)}),/antecedent mismatch/)});
test('absent assumption discharge rejected',()=>{assert.throws(()=>check({rule:'impI',assumption:B,proof:assume(A)}),/not present/)});
test('malformed conjunction AST rejected before inference',()=>{assert.throws(()=>check({rule:'andEL',proof:assume(['and',A])}),/malformed formula AST/)});
test('unknown formula operator rejected',()=>{assert.throws(()=>validateFormula(['xor',A,B]),/unknown formula operator/)});
test('formula AST wrong arity rejected',()=>{assert.throws(()=>validateFormula(['and',A,B,C]),/malformed formula AST/)});
test('empty atom rejected',()=>{assert.throws(()=>validateFormula(''),/empty atom/)});
test('object-valued atom rejected',()=>{assert.throws(()=>validateFormula({atom:'A'}),/malformed formula AST/)});
test('unexpected proof fields rejected',()=>{assert.throws(()=>check({rule:'assume',formula:A,claimedConclusion:B}),/fields do not match/)});
test('truth table catches invalid entailment A entails B',()=>{assert.equal(tautologyUnderContext(B,[A]),false)});
test('truth table confirms modus ponens',()=>{assert.equal(tautologyUnderContext(B,[['imp',A,B],A]),true)});
test('unsupported formula operator rejected by oracle',()=>{assert.throws(()=>tautologyUnderContext(['xor',A,B],[]),/unknown formula operator/)});
test('atom enumeration limit enforced',()=>{const xs=Array.from({length:MAX_ATOMS+1},(_,i)=>'P'+i);let f=xs[0];for(let i=1;i<xs.length;i++)f=['or',f,xs[i]];assert.throws(()=>tautologyUnderContext(f,[]),/atom limit exceeded/)});
test('deep formula rejected',()=>{let f=A;for(let i=0;i<260;i++)f=['and',f,A];assert.throws(()=>validateFormula(f),/depth limit exceeded/)});
test('deep proof rejected',()=>{let p=assume(A);for(let i=0;i<260;i++)p={rule:'andEL',proof:{rule:'andI',left:p,right:assume(A)}};assert.throws(()=>check(p),/proof depth limit exceeded/)});
test('duplicate assumption discharge leaves remaining occurrence',()=>{const r=check({rule:'impI',assumption:A,proof:{rule:'andI',left:assume(A),right:assume(A)}});assert.deepEqual(r.context,[A]);assert.deepEqual(r.conclusion,['imp',A,['and',A,A]]);assert.equal(tautologyUnderContext(r.conclusion,r.context),true)});
test('implication truth evaluation matches all four valuations',()=>{for(const a of [false,true])for(const b of [false,true])assert.equal(evalF(['imp',A,B],{A:a,B:b}),!a||b)});
test('claim-bound proof accepted for exact conclusion and context',()=>{assert.equal(checkBound({rule:'impI',assumption:A,proof:{rule:'assume',formula:A}},['imp',A,A],[]).context.length,0)});
test('claim substitution rejected',()=>{assert.throws(()=>checkBound({rule:'assume',formula:A},B,[A]),/claim conclusion mismatch/)});
test('assumption-context substitution rejected',()=>{assert.throws(()=>checkBound({rule:'assume',formula:A},A,[B]),/assumption context mismatch/)});
test('duplicate assumptions are preserved in context binding',()=>{assert.throws(()=>checkBound({rule:'andI',left:assume(A),right:assume(A)},['and',A,A],[A]),/assumption context mismatch/)});
test('independent semantic oracle catches mutated invalid conclusion',()=>{assert.equal(tautologyUnderContext(C,[['and',A,B]]),false)});
test('tampered proof step rejected',()=>{assert.throws(()=>verify({rule:'andEL',proof:assume(A)}),/requires conjunction/)});

test('aggregate proof and embedded-formula node budget enforced',()=>{
  const leaves=Array.from({length:3000},(_,i)=>'X'+(i%3));
  function balanced(xs){if(xs.length===1)return xs[0];const m=Math.floor(xs.length/2);return ['and',balanced(xs.slice(0,m)),balanced(xs.slice(m))];}
  const big=balanced(leaves);
  assert.throws(()=>check({rule:'andI',left:{rule:'assume',formula:big},right:{rule:'assume',formula:big}}),/input node limit exceeded/);
});
test('truth-table evaluation work budget enforced',()=>{
  const conclusion=['imp','P0','P0'];
  const context=Array.from({length:1800},(_,i)=>{const atom='P'+(i%16);return ['imp',atom,atom]});
  assert.throws(()=>tautologyUnderContext(conclusion,context),/evaluation budget exceeded/);
});


test('orIR cannot reset aggregate formula-node budget',()=>{
  const leaves=Array.from({length:2000},(_,i)=>'R'+(i%2));
  function balanced(xs){if(xs.length===1)return xs[0];const m=Math.floor(xs.length/2);return ['and',balanced(xs.slice(0,m)),balanced(xs.slice(m))];}
  const big=balanced(leaves);
  const p={rule:'orIR',proof:{rule:'orIR',proof:{rule:'orIR',proof:assume(A),other:big},other:big},other:big};
  assert.throws(()=>check(p),/input node limit exceeded/);
});
test('large truth-table formulas remain under one global evaluation budget',()=>{
  const leaves=Array.from({length:2400},()=>['imp','P0','P0']);
  function balancedOr(xs){if(xs.length===1)return xs[0];const m=Math.floor(xs.length/2);return ['or',balancedOr(xs.slice(0,m)),balancedOr(xs.slice(m))];}
  const largeTautology=balancedOr(leaves);
  const context=[largeTautology,...Array.from({length:16},(_,i)=>['imp','P'+i,'P'+i])];
  assert.throws(()=>tautologyUnderContext(['imp','P0','P0'],context),/evaluation budget exceeded/);
});


test('oversized atom rejected before proof comparison',()=>{
  assert.throws(()=>validateFormula('X'.repeat(MAX_ATOM_LENGTH+1)),/atom length limit exceeded/);
});
test('oversized rule label rejected',()=>{
  assert.throws(()=>check({rule:'R'.repeat(MAX_RULE_LENGTH+1),formula:A}),/rule length limit exceeded/);
});


test('truth assignment requires an own Boolean value',()=>{
  assert.equal(evalF(A,{A:false}),false);
  assert.equal(evalF(A,{A:true}),true);
  assert.throws(()=>evalF('toString',{}),/missing truth assignment/);
  assert.throws(()=>evalF(A,Object.create({A:true})),/missing truth assignment/);
  assert.throws(()=>evalF(A,{A:'false'}),/truth assignment must be boolean/);
  assert.throws(()=>evalF(A,null),/environment must be an object/);
  assert.throws(()=>evalF(A,[true]),/environment must be an object/);
});
test('cyclic formula AST fails closed at depth limit',()=>{
  const f=['and','A','A'];f[1]=f;
  assert.throws(()=>validateFormula(f),/formula depth limit exceeded/);
});
test('cyclic proof object fails closed at depth limit',()=>{
  const p={rule:'andEL'};p.proof=p;
  assert.throws(()=>check(p),/proof depth limit exceeded/);
});
test('very wide proof object is rejected by schema-size gate',()=>{
  const p={rule:'assume',formula:A};
  for(let i=0;i<1000;i++)p['extra'+i]=i;
  assert.throws(()=>check(p),/proof fields do not match rule schema/);
});


test('proof accessors are rejected without invoking getters',()=>{
  let calls=0;const p={};
  Object.defineProperty(p,'rule',{enumerable:true,get(){calls++;return 'assume'}});
  Object.defineProperty(p,'formula',{enumerable:true,get(){calls++;return A}});
  assert.throws(()=>check(p),/proof node accessors are not allowed/);
  assert.equal(calls,0);
});
test('formula AST accessors are rejected without invoking getters',()=>{
  let calls=0;const f=['and',A,B];
  Object.defineProperty(f,'1',{enumerable:true,configurable:true,get(){calls++;return A}});
  assert.throws(()=>validateFormula(f),/formula AST accessors are not allowed/);
  assert.equal(calls,0);
});
test('truth assignment accessors are rejected without invoking getters',()=>{
  let calls=0;const env={};
  Object.defineProperty(env,A,{enumerable:true,get(){calls++;return true}});
  assert.throws(()=>evalF(A,env),/truth assignment accessors are not allowed/);
  assert.equal(calls,0);
});
test('claim context rejects sparse arrays',()=>{
  const sparse=[];sparse.length=2;sparse[1]=A;
  assert.throws(()=>checkBound(assume(A),A,sparse),/dense/);
});


test('proof schema cannot hide an own __proto__ field during normalization',()=>{
  const p={rule:'assume',formula:A};
  Object.defineProperty(p,'__proto__',{value:{unexpected:true},enumerable:true,configurable:true,writable:true});
  assert.throws(()=>check(p),/fields do not match/);
});


test('formula AST arrays reject custom keys, custom prototypes, and sparse slots',()=>{
  const extra=['and',A,B];extra.note='unexpected';
  assert.throws(()=>validateFormula(extra),/no custom properties/);
  const sparse=['and',A,B];delete sparse[1];
  assert.throws(()=>validateFormula(sparse),/dense/);
  const custom=Object.setPrototypeOf(['and',A,B],Object.create(Array.prototype));
  assert.throws(()=>validateFormula(custom),/ordinary array/);
});


test('checked conclusion is detached from caller-owned formula arrays',()=>{
  const source=['and',A,B];
  const result=check({rule:'assume',formula:source});
  source[1]='MUTATED';
  assert.deepEqual(result.conclusion,['and',A,B]);
  assert.deepEqual(result.context[0],['and',A,B]);
});
test('checked derivation result is recursively frozen',()=>{
  const result=check(assume(['and',A,B]));
  assert.equal(Object.isFrozen(result),true);
  assert.equal(Object.isFrozen(result.conclusion),true);
  assert.equal(Object.isFrozen(result.context),true);
  assert.equal(Object.isFrozen(result.context[0]),true);
  assert.throws(()=>{result.conclusion[1]='MUTATED';},TypeError);
});
test('disjunction introduction copies auxiliary formula before returning result',()=>{
  const other=['and',A,B];
  const result=check({rule:'orIR',proof:assume(A),other});
  other[1]='MUTATED';
  assert.deepEqual(result.conclusion,['or',['and',A,B],A]);
});


test('public formula validator does not accept caller-controlled node budgets',()=>{
  function full(depth){return depth===0?A:['and',full(depth-1),full(depth-1)];}
  const large=full(13);
  assert.throws(()=>validateFormula(large,0,{nodes:-1000000000}),/input node limit exceeded/);
});
test('public proof checker does not accept caller-controlled node budgets',()=>{
  function proof(depth){return depth===0?assume(A):{rule:'andI',left:proof(depth-1),right:proof(depth-1)};}
  assert.throws(()=>check(proof(13),{nodes:-1000000000}),/input node limit exceeded/);
});
test('public evaluator ignores caller-supplied work-counter objects',()=>{
  let reads=0,writes=0;
  const steps={get count(){reads++;return 0;},set count(_){writes++;}};
  assert.equal(evalF(A,{A:true},steps),true);
  assert.equal(reads,0);
  assert.equal(writes,0);
});


test('formula validation and certificate copying share one aggregate budget',()=>{
  const leaves=Array.from({length:2600},(_,i)=>'F'+(i%2));
  function balanced(xs){if(xs.length===1)return xs[0];const m=Math.floor(xs.length/2);return ['and',balanced(xs.slice(0,m)),balanced(xs.slice(m))];}
  const formula=balanced(leaves);
  assert.throws(()=>check({rule:'assume',formula}),/input node limit exceeded/);
});


test('bounded validation collects truth-table atoms without a second AST walk',()=>{
  const leaves=Array.from({length:1500},()=>['imp','P0','P0']);
  function balancedOr(xs){if(xs.length===1)return xs[0];const m=Math.floor(xs.length/2);return ['or',balancedOr(xs.slice(0,m)),balancedOr(xs.slice(m))];}
  const formula=balancedOr(leaves);
  assert.equal(tautologyUnderContext(formula,[]),true);
});

test('aggregate kernel work budget bounds repeated long-formula context discharge',()=>{
  const count=2100;
  const atoms=Array.from({length:count},(_,i)=>String(i).padStart(4,'0')+'X'.repeat(MAX_ATOM_LENGTH-4));
  function balanced(xs){
    if(xs.length===1)return {rule:'assume',formula:xs[0]};
    const m=Math.floor(xs.length/2);
    return {rule:'andI',left:balanced(xs.slice(0,m)),right:balanced(xs.slice(m))};
  }
  let proof=balanced(atoms);
  for(let i=count-1;i>=count-100;i--) proof={rule:'impI',assumption:atoms[i],proof};
  assert.throws(()=>check(proof),/kernel work budget exceeded/);
});

console.log(JSON.stringify({passed,failed,total:passed+failed,results},null,2));
if(failed)process.exitCode=1;
