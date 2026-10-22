'use strict';
// Hardened educational reference kernel. Not production-certified.
const MAX_DEPTH = 256;
const MAX_NODES = 10000;
const MAX_ATOMS = 16;
const MAX_EVAL_STEPS = 2000000;
const MAX_ATOM_LENGTH = 4096;
const MAX_RULE_LENGTH = 32;
const eq = (a,b) => JSON.stringify(a) === JSON.stringify(b);
const union = (a,b) => [...a,...b];

// Treat proof inputs as inert, JSON-like data. Inspect descriptors before any
// field read so an accessor cannot execute during validation.
function readDataObject(value, label) {
  if (!value || typeof value !== 'object' || Array.isArray(value) ||
      Object.getPrototypeOf(value) !== Object.prototype) {
    throw new Error(`${label} must be a plain object`);
  }
  const keys = Reflect.ownKeys(value);
  // Every supported proof rule has at most four fields; reject width before
  // descriptor reads and normalization of attacker-supplied extra fields.
  if (keys.length > 4) throw new Error('proof fields do not match rule schema');
  if (keys.some(key => typeof key !== 'string')) {
    throw new Error(`${label} has a non-string field`);
  }
  const out = {};
  for (const key of keys) {
    const descriptor = Object.getOwnPropertyDescriptor(value, key);
    if (!descriptor || !Object.prototype.hasOwnProperty.call(descriptor, 'value')) {
      throw new Error(`${label} accessors are not allowed`);
    }
    if (!descriptor.enumerable) {
      throw new Error(`${label} fields must be enumerable`);
    }
    Object.defineProperty(out, key, { value: descriptor.value, enumerable: true, configurable: true, writable: true });
  }
  return out;
}

function readDataArray(value, label) {
  if (!Array.isArray(value) || Object.getPrototypeOf(value) !== Array.prototype) {
    throw new Error(`${label} must be an ordinary array`);
  }
  if (value.length > MAX_NODES) throw new Error(`${label} exceeds item limit`);
  const keys = Reflect.ownKeys(value);
  if (keys.length !== value.length + 1 ||
      keys.some(key => key !== 'length' && (typeof key !== 'string' ||
        !/^(0|[1-9][0-9]*)$/.test(key) || Number(key) >= value.length))) {
    throw new Error(`${label} must be dense and have no custom properties`);
  }
  const out = [];
  for (let i = 0; i < value.length; i++) {
    const descriptor = Object.getOwnPropertyDescriptor(value, String(i));
    if (!descriptor) throw new Error(`${label} must be dense`);
    if (!Object.prototype.hasOwnProperty.call(descriptor, 'value')) {
      throw new Error(`${label} accessors are not allowed`);
    }
    if (!descriptor.enumerable) {
      throw new Error(`${label} elements must be enumerable`);
    }
    out.push(descriptor.value);
  }
  return out;
}

function copyFormula(formula, depth=0, budget={nodes:0}) {
  if (depth > MAX_DEPTH) throw new Error('formula depth limit exceeded');
  if (++budget.nodes > MAX_NODES) throw new Error('input node limit exceeded');
  if (typeof formula === 'string') {
    if (formula.length === 0 || formula.length > MAX_ATOM_LENGTH) throw new Error('invalid formula atom');
    return formula;
  }
  if (!Array.isArray(formula)) throw new Error('malformed formula AST');
  const parts = readDataArray(formula, 'formula AST');
  if (parts.length !== 3) throw new Error('malformed formula AST');
  const [op,left,right] = parts;
  if (!['and','or','imp'].includes(op)) throw new Error('unknown formula operator');
  return [op,copyFormula(left,depth+1,budget),copyFormula(right,depth+1,budget)];
}

function freezeResult(value) {
  if (value && typeof value === 'object' && !Object.isFrozen(value)) {
    for (const key of Object.keys(value)) freezeResult(value[key]);
    Object.freeze(value);
  }
  return value;
}

function validateFormula(formula, depth=0, budget={nodes:0}) {
  if (depth > MAX_DEPTH) throw new Error('formula depth limit exceeded');
  if (++budget.nodes > MAX_NODES) throw new Error('input node limit exceeded');
  if (typeof formula === 'string') {
    if (formula.length === 0) throw new Error('empty atom');
    if (formula.length > MAX_ATOM_LENGTH) throw new Error('atom length limit exceeded');
    return true;
  }
  if (!Array.isArray(formula)) throw new Error('malformed formula AST');
  const parts = readDataArray(formula, 'formula AST');
  if (parts.length !== 3) throw new Error('malformed formula AST');
  const [op,left,right] = parts;
  if (!['and','or','imp'].includes(op)) throw new Error('unknown formula operator');
  validateFormula(left,depth+1,budget);
  validateFormula(right,depth+1,budget);
  return true;
}
function check(proof, budget={nodes:0}) {
  function visit(p,depth) {
    if (depth > MAX_DEPTH) throw new Error('proof depth limit exceeded');
    if (++budget.nodes > MAX_NODES) throw new Error('input node limit exceeded');
    const data = readDataObject(p, 'proof node');
    const keys = Object.keys(data);
    if(keys.length>4) throw new Error('proof fields do not match rule schema');
    keys.sort();
    const requireKeys=(expected) => {
      if (JSON.stringify(keys) !== JSON.stringify([...expected].sort())) throw new Error('proof fields do not match rule schema');
    };
    if (typeof data.rule !== 'string') throw new Error('missing proof rule');
    if (data.rule.length > MAX_RULE_LENGTH) throw new Error('proof rule length limit exceeded');
    switch(data.rule) {
      case 'assume':
        requireKeys(['rule','formula']);
        validateFormula(data.formula,0,budget);
        const formula=copyFormula(data.formula);
        return {conclusion:formula,context:[formula]};
      case 'andI': {
        requireKeys(['rule','left','right']);
        const a=visit(data.left,depth+1),b=visit(data.right,depth+1);
        return {conclusion:['and',a.conclusion,b.conclusion],context:union(a.context,b.context)};
      }
      case 'andEL': {
        requireKeys(['rule','proof']);
        const a=visit(data.proof,depth+1);
        if (!Array.isArray(a.conclusion) || a.conclusion[0]!=='and') throw new Error('andEL requires conjunction');
        return {conclusion:a.conclusion[1],context:a.context};
      }
      case 'andER': {
        requireKeys(['rule','proof']);
        const a=visit(data.proof,depth+1);
        if (!Array.isArray(a.conclusion) || a.conclusion[0]!=='and') throw new Error('andER requires conjunction');
        return {conclusion:a.conclusion[2],context:a.context};
      }
      case 'impI': {
        requireKeys(['rule','assumption','proof']);
        validateFormula(data.assumption,0,budget);
        const assumption=copyFormula(data.assumption);
        const a=visit(data.proof,depth+1);
        const i=a.context.findIndex(x=>eq(x,assumption));
        if(i<0) throw new Error('impI assumption not present for discharge');
        const ctx=[...a.context];ctx.splice(i,1);
        return {conclusion:['imp',assumption,a.conclusion],context:ctx};
      }
      case 'impE': {
        requireKeys(['rule','function','argument']);
        const a=visit(data.function,depth+1),b=visit(data.argument,depth+1);
        if(!Array.isArray(a.conclusion)||a.conclusion[0]!=='imp'||!eq(a.conclusion[1],b.conclusion)) throw new Error('impE antecedent mismatch');
        return {conclusion:a.conclusion[2],context:union(a.context,b.context)};
      }
      case 'orIL': {
        requireKeys(['rule','proof','other']);
        validateFormula(data.other,0,budget);
        const other=copyFormula(data.other);
        const a=visit(data.proof,depth+1);
        return {conclusion:['or',a.conclusion,other],context:a.context};
      }
      case 'orIR': {
        requireKeys(['rule','proof','other']);
        validateFormula(data.other,0,budget);
        const other=copyFormula(data.other);
        const a=visit(data.proof,depth+1);
        return {conclusion:['or',other,a.conclusion],context:a.context};
      }
      default: throw new Error('unknown inference rule');
    }
  }
  return freezeResult(visit(proof,0));
}
function checkBound(proof, expectedConclusion, expectedContext) {
  const budget={nodes:0};
  validateFormula(expectedConclusion,0,budget);
  if (!Array.isArray(expectedContext)) throw new Error('expected context must be an array');
  const contextValues=readDataArray(expectedContext, 'expected context');
  contextValues.forEach(f=>validateFormula(f,0,budget));
  const result=check(proof,budget);
  if (!eq(result.conclusion,expectedConclusion)) throw new Error('claim conclusion mismatch');
  const canon=xs=>xs.map(x=>JSON.stringify(x)).sort();
  if (!eq(canon(result.context),canon(contextValues))) throw new Error('assumption context mismatch');
  return result;
}
function atoms(formula,out=new Set(),budget={nodes:0}) {
  validateFormula(formula,0,budget);
  function walk(f){if(typeof f==='string')out.add(f);else {walk(f[1]);walk(f[2]);}}
  walk(formula);
  return out;
}
function evaluateValidated(formula,env,steps) {
  function tick(){if(++steps.count>MAX_EVAL_STEPS)throw new Error('truth-table evaluation budget exceeded');}
  function walk(f) {
    tick();
    if(typeof f==='string') {
      if(!env || typeof env!=='object' || Array.isArray(env)) throw new Error('truth assignment environment must be an object');
      const descriptor = Object.getOwnPropertyDescriptor(env, f);
      if (!descriptor) throw new Error('missing truth assignment for atom');
      if (!Object.prototype.hasOwnProperty.call(descriptor, 'value')) throw new Error('truth assignment accessors are not allowed');
      if(typeof descriptor.value!=='boolean') throw new Error('truth assignment must be boolean');
      return descriptor.value;
    }
    const [op,a,b]=f;
    if(op==='and') return walk(a)&&walk(b);
    if(op==='or') return walk(a)||walk(b);
    if(op==='imp') return !walk(a)||walk(b);
    throw new Error('unknown formula operator');
  }
  return walk(formula);
}
function evalF(formula,env,steps={count:0}) {
  if(!env || typeof env!=='object' || Array.isArray(env)) throw new Error('truth assignment environment must be an object');
  validateFormula(formula);
  return evaluateValidated(formula,env,steps);
}
function tautologyUnderContext(conclusion,context) {
  const inputBudget={nodes:0};
  validateFormula(conclusion,0,inputBudget);
  if(!Array.isArray(context)) throw new Error('context must be an array');
  const contextValues=readDataArray(context, 'context');
  for(const f of contextValues) validateFormula(f,0,inputBudget);
  const collect=f=>{const out=new Set();(function walk(x){if(typeof x==='string')out.add(x);else{walk(x[1]);walk(x[2]);}})(f);return out;};
  const names=[...new Set([...collect(conclusion),...contextValues.flatMap(f=>[...collect(f)])])];
  if(names.length>MAX_ATOMS) throw new Error('truth-table atom limit exceeded');
  const steps={count:0};
  for(let mask=0;mask<(1<<names.length);mask++){
    const env=Object.fromEntries(names.map((n,i)=>[n,!!(mask&(1<<i))]));
    if(contextValues.every(f=>evaluateValidated(f,env,steps))&&!evaluateValidated(conclusion,env,steps)) return false;
  }
  return true;
}
module.exports={MAX_DEPTH,MAX_NODES,MAX_ATOMS,MAX_EVAL_STEPS,MAX_ATOM_LENGTH,MAX_RULE_LENGTH,validateFormula,check,checkBound,eq,evalF,tautologyUnderContext};
