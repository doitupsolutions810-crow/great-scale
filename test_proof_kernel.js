'use strict';
const assert=require('node:assert/strict');
const {check,tautologyUnderContext}=require('./proof_kernel');
const A='A', B='B', C='C';
const tests=[];
function test(name,fn){try{fn();tests.push({name,ok:true})}catch(e){tests.push({name,ok:false,error:e.message})}}
function verifyProof(proof){const r=check(proof);assert.equal(tautologyUnderContext(r.conclusion,r.context),true, 'accepted proof failed truth-table oracle');return r}
test('assumption is accepted only under itself',()=>{const r=verifyProof({rule:'assume',formula:A});assert.deepEqual(r.context,[A]);assert.equal(r.conclusion,A)});
test('conjunction introduction is semantically sound',()=>{const r=verifyProof({rule:'andI',left:{rule:'assume',formula:A},right:{rule:'assume',formula:B}});assert.deepEqual(r.conclusion,['and',A,B])});
test('left conjunction elimination',()=>{const p={rule:'andEL',proof:{rule:'andI',left:{rule:'assume',formula:A},right:{rule:'assume',formula:B}}};assert.equal(verifyProof(p).conclusion,A)});
test('right conjunction elimination',()=>{const p={rule:'andER',proof:{rule:'andI',left:{rule:'assume',formula:A},right:{rule:'assume',formula:B}}};assert.equal(verifyProof(p).conclusion,B)});
test('implication introduction discharges assumption',()=>{const r=verifyProof({rule:'impI',assumption:A,proof:{rule:'assume',formula:A}});assert.deepEqual(r.conclusion,['imp',A,A]);assert.deepEqual(r.context,[])});
test('modus ponens',()=>{const p={rule:'impE',function:{rule:'assume',formula:['imp',A,B]},argument:{rule:'assume',formula:A}};const r=verifyProof(p);assert.equal(r.conclusion,B);assert.equal(r.context.length,2)});
test('left disjunction introduction',()=>{const r=verifyProof({rule:'orIL',proof:{rule:'assume',formula:A},other:B});assert.deepEqual(r.conclusion,['or',A,B])});
test('right disjunction introduction',()=>{const r=verifyProof({rule:'orIR',proof:{rule:'assume',formula:B},other:A});assert.deepEqual(r.conclusion,['or',A,B])});
test('rejects unknown inference rule',()=>{assert.throws(()=>check({rule:'magic',formula:A}),/unknown inference rule/)});
test('rejects conjunction elimination on atom',()=>{assert.throws(()=>check({rule:'andEL',proof:{rule:'assume',formula:A}}),/requires conjunction/)});
test('rejects invalid modus ponens antecedent',()=>{assert.throws(()=>check({rule:'impE',function:{rule:'assume',formula:['imp',A,B]},argument:{rule:'assume',formula:C}}),/antecedent mismatch/)});
test('rejects implication discharge of absent assumption',()=>{assert.throws(()=>check({rule:'impI',assumption:B,proof:{rule:'assume',formula:A}}),/not present/)});
test('truth-table oracle catches false implication',()=>{assert.equal(tautologyUnderContext(['imp',A,B],[A]),false)});
test('truth-table oracle confirms valid modus ponens consequence',()=>{assert.equal(tautologyUnderContext(B,[['imp',A,B],A]),true)});
test('truth-table oracle catches excluded-middle claim if operator unsupported',()=>{assert.throws(()=>tautologyUnderContext(['xor',A,B],[]),/unknown formula operator/)});
test('tampered proof rule is rejected',()=>{const p={rule:'andEL',proof:{rule:'assume',formula:A}};assert.throws(()=>verifyProof(p),/requires conjunction/)});
for(const t of tests)console.log((t.ok?'PASS ':'FAIL ')+t.name+(t.error?' — '+t.error:''));
console.log('\n'+tests.filter(t=>t.ok).length+'/'+tests.length+' passed');
if(tests.some(t=>!t.ok))process.exitCode=1;
