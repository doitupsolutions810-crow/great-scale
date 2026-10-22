'use strict';
// Hardened educational reference kernel. Not production-certified.
const MAX_DEPTH = 256;
const MAX_NODES = 10000;
const MAX_ATOMS = 16;
const MAX_EVAL_STEPS = 2000000;
const MAX_KERNEL_WORK = 2000000;
const MAX_ATOM_LENGTH = 4096;
const MAX_INPUT_BYTES = 1048576;
const MAX_RULE_LENGTH = 32;
const eq = (a,b) => JSON.stringify(a) === JSON.stringify(b);
function tickKernelWork(budget, amount=1) {
  budget.work = (budget.work || 0) + amount;
  if (budget.work > MAX_KERNEL_WORK) throw new Error('kernel work budget exceeded');
}
function formulaEquals(a,b,budget) {
  if (typeof a === 'string' || typeof b === 'string') {
    const aLength = typeof a === 'string' ? a.length : 0;
    const bLength = typeof b === 'string' ? b.length : 0;
    tickKernelWork(budget, Math.max(aLength,bLength)+1);
    return typeof a === typeof b && a === b;
  }
  tickKernelWork(budget);
  if (!Array.isArray(a) || !Array.isArray(b) || a.length !== b.length) return false;
  for (let i=0;i<a.length;i++) if (!formulaEquals(a[i],b[i],budget)) return false;
  return true;
}
function union(a,b,budget) {
  tickKernelWork(budget,a.length+b.length);
  return [...a,...b];
}
function sameFormulaMultiset(a,b,budget) {
  if (a.length !== b.length) return false;
  tickKernelWork(budget,b.length);
  const used = new Array(b.length).fill(false);
  for (const formula of a) {
    let found = -1;
    for (let i=0;i<b.length;i++) {
      tickKernelWork(budget);
      if (!used[i] && formulaEquals(formula,b[i],budget)) { found=i; break; }
    }
    if (found < 0) return false;
    used[found]=true;
  }
  return true;
}

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

function validateFormulaInternal(formula, depth=0, budget={nodes:0}, atomSet=null) {
  if (depth > MAX_DEPTH) throw new Error('formula depth limit exceeded');
  if (++budget.nodes > MAX_NODES) throw new Error('input node limit exceeded');
  if (typeof formula === 'string') {
    if (formula.length === 0) throw new Error('empty atom');
    if (formula.length > MAX_ATOM_LENGTH) throw new Error('atom length limit exceeded');
    if (atomSet) atomSet.add(formula);
    return true;
  }
  if (!Array.isArray(formula)) throw new Error('malformed formula AST');
  const parts = readDataArray(formula, 'formula AST');
  if (parts.length !== 3) throw new Error('malformed formula AST');
  const [op,left,right] = parts;
  if (!['and','or','imp'].includes(op)) throw new Error('unknown formula operator');
  validateFormulaInternal(left,depth+1,budget,atomSet);
  validateFormulaInternal(right,depth+1,budget,atomSet);
  return true;
}
function validateFormula(formula) {
  return validateFormulaInternal(formula,0,{nodes:0});
}

function checkInternal(proof, budget={nodes:0,work:0}) {
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
        validateFormulaInternal(data.formula,0,budget);
        const formula=copyFormula(data.formula,0,budget);
        return {conclusion:formula,context:[formula]};
      case 'andI': {
        requireKeys(['rule','left','right']);
        const a=visit(data.left,depth+1),b=visit(data.right,depth+1);
        return {conclusion:['and',a.conclusion,b.conclusion],context:union(a.context,b.context,budget)};
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
        validateFormulaInternal(data.assumption,0,budget);
        const assumption=copyFormula(data.assumption,0,budget);
        const a=visit(data.proof,depth+1);
        let i=-1;
        for(let j=0;j<a.context.length;j++) {
          if(formulaEquals(a.context[j],assumption,budget)) { i=j; break; }
        }
        if(i<0) throw new Error('impI assumption not present for discharge');
        tickKernelWork(budget,a.context.length);
        const ctx=[...a.context];
        tickKernelWork(budget,Math.max(0,ctx.length-i-1));
        ctx.splice(i,1);
        return {conclusion:['imp',assumption,a.conclusion],context:ctx};
      }
      case 'impE': {
        requireKeys(['rule','function','argument']);
        const a=visit(data.function,depth+1),b=visit(data.argument,depth+1);
        if(!Array.isArray(a.conclusion)||a.conclusion[0]!=='imp'||!formulaEquals(a.conclusion[1],b.conclusion,budget)) throw new Error('impE antecedent mismatch');
        return {conclusion:a.conclusion[2],context:union(a.context,b.context,budget)};
      }
      case 'orIL': {
        requireKeys(['rule','proof','other']);
        validateFormulaInternal(data.other,0,budget);
        const other=copyFormula(data.other,0,budget);
        const a=visit(data.proof,depth+1);
        return {conclusion:['or',a.conclusion,other],context:a.context};
      }
      case 'orIR': {
        requireKeys(['rule','proof','other']);
        validateFormulaInternal(data.other,0,budget);
        const other=copyFormula(data.other,0,budget);
        const a=visit(data.proof,depth+1);
        return {conclusion:['or',other,a.conclusion],context:a.context};
      }
      default: throw new Error('unknown inference rule');
    }
  }
  return freezeResult(visit(proof,0));
}
function check(proof) {
  return checkInternal(proof,{nodes:0});
}
function checkBound(proof, expectedConclusion, expectedContext) {
  const budget={nodes:0,work:0};
  validateFormulaInternal(expectedConclusion,0,budget);
  if (!Array.isArray(expectedContext)) throw new Error('expected context must be an array');
  const contextValues=readDataArray(expectedContext, 'expected context');
  contextValues.forEach(f=>validateFormulaInternal(f,0,budget));
  const result=checkInternal(proof,budget);
  if (!formulaEquals(result.conclusion,expectedConclusion,budget)) throw new Error('claim conclusion mismatch');
  if (!sameFormulaMultiset(result.context,contextValues,budget)) throw new Error('assumption context mismatch');
  return result;
}

// JSON.parse accepts duplicate object keys and silently keeps the last value.
// Scan the already-size-bounded, already-syntax-validated JSON iteratively so
// security-sensitive envelopes have one unambiguous interpretation.
function rejectDuplicateJsonKeys(input) {
  const stack = [];
  let i = 0;
  let rootDone = false;
  const skipSpace = () => { while (i < input.length && /\\s/.test(input[i])) i++; };
  const stringEnd = start => {
    let j = start + 1;
    while (j < input.length) {
      if (input[j] === '\\\\') { j += 2; continue; }
      if (input[j] === '"') return j + 1;
      j++;
    }
    return input.length;
  };
  while (true) {
    skipSpace();
    if (i >= input.length) break;
    const frame = stack[stack.length - 1];
    if (frame && frame.type === 'object' && (frame.state === 'keyOrEnd' || frame.state === 'key')) {
      if (input[i] === '}') { stack.pop(); i++; continue; }
      const end = stringEnd(i);
      const key = JSON.parse(input.slice(i, end));
      if (frame.keys.has(key)) throw new Error('duplicate JSON object key');
      frame.keys.add(key);
      frame.state = 'colon';
      i = end;
      continue;
    }
    if (frame && frame.type === 'object' && frame.state === 'colon') {
      i++; // JSON.parse has already established that this is ':'
      frame.state = 'value';
      continue;
    }
    if (frame && frame.state === 'commaOrEnd') {
      if (input[i] === ',') {
        i++;
        frame.state = frame.type === 'object' ? 'key' : 'value';
      } else {
        stack.pop();
        i++; // closing brace/bracket, already validated by JSON.parse
      }
      continue;
    }
    if (frame && frame.type === 'array' && frame.state === 'valueOrEnd' && input[i] === ']') {
      stack.pop(); i++; continue;
    }
    if (!frame && rootDone) break;

    // A value begins here. Mark the containing frame before descending.
    if (frame) frame.state = 'commaOrEnd';
    else rootDone = true;
    if (input[i] === '{') {
      stack.push({type:'object', state:'keyOrEnd', keys:new Set()});
      i++;
    } else if (input[i] === '[') {
      stack.push({type:'array', state:'valueOrEnd'});
      i++;
    } else if (input[i] === '"') {
      i = stringEnd(i);
    } else {
      while (i < input.length && !/[\\s,\\]}]/.test(input[i])) i++;
    }
  }
}

function parseBoundedJson(input) {
  if (typeof input !== 'string') throw new Error('serialized input must be a string');
  // Bound code units before the UTF-8 scan, then enforce the actual byte limit.
  if (input.length > MAX_INPUT_BYTES || Buffer.byteLength(input, 'utf8') > MAX_INPUT_BYTES) {
    throw new Error('serialized input byte limit exceeded');
  }
  let parsed;
  try {
    parsed = JSON.parse(input);
  } catch {
    throw new Error('serialized input is not valid JSON');
  }
  rejectDuplicateJsonKeys(input);
  return parsed;
}
function requireEnvelopeKeys(envelope, expected, label) {
  const data = readDataObject(envelope, label);
  const keys = Object.keys(data).sort();
  if (JSON.stringify(keys) !== JSON.stringify([...expected].sort())) {
    throw new Error(label + ' fields do not match schema');
  }
  return data;
}
function checkSerialized(input) {
  return check(parseBoundedJson(input));
}
function checkBoundSerialized(input) {
  const envelope = requireEnvelopeKeys(parseBoundedJson(input),
    ['proof','expectedConclusion','expectedContext'], 'claim envelope');
  return checkBound(envelope.proof, envelope.expectedConclusion, envelope.expectedContext);
}
function tautologyUnderContextSerialized(input) {
  const envelope = requireEnvelopeKeys(parseBoundedJson(input),
    ['conclusion','context'], 'truth-table envelope');
  return tautologyUnderContext(envelope.conclusion, envelope.context);
}

function atoms(formula,out=new Set(),budget={nodes:0}) {
  validateFormulaInternal(formula,0,budget);
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
function evalFInternal(formula,env,steps) {
  if(!env || typeof env!=='object' || Array.isArray(env)) throw new Error('truth assignment environment must be an object');
  validateFormulaInternal(formula,0,{nodes:0});
  return evaluateValidated(formula,env,steps);
}
function evalF(formula,env) {
  return evalFInternal(formula,env,{count:0});
}
function tautologyUnderContext(conclusion,context) {
  const inputBudget={nodes:0};
  const namesSet=new Set();
  validateFormulaInternal(conclusion,0,inputBudget,namesSet);
  if(!Array.isArray(context)) throw new Error('context must be an array');
  const contextValues=readDataArray(context, 'context');
  for(const f of contextValues) validateFormulaInternal(f,0,inputBudget,namesSet);
  // Atom discovery is fused into the bounded validation traversal: no second
  // recursive walk over attacker-controlled formulas is needed.
  const names=[...namesSet];
  if(names.length>MAX_ATOMS) throw new Error('truth-table atom limit exceeded');
  const steps={count:0};
  for(let mask=0;mask<(1<<names.length);mask++){
    const env=Object.fromEntries(names.map((n,i)=>[n,!!(mask&(1<<i))]));
    if(contextValues.every(f=>evaluateValidated(f,env,steps))&&!evaluateValidated(conclusion,env,steps)) return false;
  }
  return true;
}
module.exports={MAX_DEPTH,MAX_NODES,MAX_ATOMS,MAX_EVAL_STEPS,MAX_ATOM_LENGTH,MAX_INPUT_BYTES,MAX_RULE_LENGTH,validateFormula,check,checkBound,checkSerialized,checkBoundSerialized,eq,evalF,tautologyUnderContext,tautologyUnderContextSerialized};
