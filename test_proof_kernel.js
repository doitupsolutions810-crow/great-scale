'use strict';
const assert=require('node:assert/strict');
const {MAX_ATOMS,MAX_EVAL_STEPS,MAX_NODES,validateFormula,check,checkBound,tautologyUnderContext,evalF}=require('./proof_kernel');
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
  const leaves=Array.from({length:2400},()=>['imp','A','A']);
  function balancedOr(xs){if(xs.length===1)return xs[0];const m=Math.floor(xs.length/2);return ['or',balancedOr(xs.slice(0,m)),balancedOr(xs.slice(m))];}
  const largeTautology=balancedOr(leaves);
  const context=[largeTautology,...Array.from({length:16},(_,i)=>['imp','P'+i,'P'+i])];
  assert.throws(()=>tautologyUnderContext('P0',context),/evaluation budget exceeded/);
});

console.log(JSON.stringify({passed,failed,total:passed+failed,results},null,2));
if(failed)process.exitCode=1;
