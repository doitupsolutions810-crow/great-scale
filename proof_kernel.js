'use strict';
// Hardened educational reference kernel. Not production-certified.
const MAX_DEPTH = 256;
const MAX_NODES = 10000;
const MAX_ATOMS = 16;
const MAX_EVAL_STEPS = 2000000;
const eq = (a,b) => JSON.stringify(a) === JSON.stringify(b);
const union = (a,b) => [...a,...b];

function validateFormula(formula, depth=0, budget={nodes:0}) {
  if (depth > MAX_DEPTH) throw new Error('formula depth limit exceeded');
  if (++budget.nodes > MAX_NODES) throw new Error('input node limit exceeded');
  if (typeof formula === 'string') {
    if (formula.length === 0) throw new Error('empty atom');
    return true;
  }
  if (!Array.isArray(formula) || formula.length !== 3) throw new Error('malformed formula AST');
  const [op,left,right] = formula;
  if (!['and','or','imp'].includes(op)) throw new Error('unknown formula operator');
  validateFormula(left,depth+1,budget);
  validateFormula(right,depth+1,budget);
  return true;
}
function check(proof, budget={nodes:0}) {
  function visit(p,depth) {
    if (depth > MAX_DEPTH) throw new Error('proof depth limit exceeded');
    if (++budget.nodes > MAX_NODES) throw new Error('input node limit exceeded');
    if (!p || typeof p !== 'object' || Array.isArray(p)) throw new Error('malformed proof');
    const keys=Object.keys(p).sort();
    const requireKeys=(expected) => {
      if (JSON.stringify(keys) !== JSON.stringify([...expected].sort())) throw new Error('proof fields do not match rule schema');
    };
    if (typeof p.rule !== 'string') throw new Error('missing proof rule');
    switch(p.rule) {
      case 'assume':
        requireKeys(['rule','formula']);
        validateFormula(p.formula,0,budget);
        return {conclusion:p.formula,context:[p.formula]};
      case 'andI': {
        requireKeys(['rule','left','right']);
        const a=visit(p.left,depth+1),b=visit(p.right,depth+1);
        return {conclusion:['and',a.conclusion,b.conclusion],context:union(a.context,b.context)};
      }
      case 'andEL': {
        requireKeys(['rule','proof']);
        const a=visit(p.proof,depth+1);
        if (!Array.isArray(a.conclusion) || a.conclusion[0]!=='and') throw new Error('andEL requires conjunction');
        return {conclusion:a.conclusion[1],context:a.context};
      }
      case 'andER': {
        requireKeys(['rule','proof']);
        const a=visit(p.proof,depth+1);
        if (!Array.isArray(a.conclusion) || a.conclusion[0]!=='and') throw new Error('andER requires conjunction');
        return {conclusion:a.conclusion[2],context:a.context};
      }
      case 'impI': {
        requireKeys(['rule','assumption','proof']);
        validateFormula(p.assumption,0,budget);
        const a=visit(p.proof,depth+1);
        const i=a.context.findIndex(x=>eq(x,p.assumption));
        if(i<0) throw new Error('impI assumption not present for discharge');
        const ctx=[...a.context];ctx.splice(i,1);
        return {conclusion:['imp',p.assumption,a.conclusion],context:ctx};
      }
      case 'impE': {
        requireKeys(['rule','function','argument']);
        const a=visit(p.function,depth+1),b=visit(p.argument,depth+1);
        if(!Array.isArray(a.conclusion)||a.conclusion[0]!=='imp'||!eq(a.conclusion[1],b.conclusion)) throw new Error('impE antecedent mismatch');
        return {conclusion:a.conclusion[2],context:union(a.context,b.context)};
      }
      case 'orIL': {
        requireKeys(['rule','proof','other']);
        validateFormula(p.other,0,budget);
        const a=visit(p.proof,depth+1);
        return {conclusion:['or',a.conclusion,p.other],context:a.context};
      }
      case 'orIR': {
        requireKeys(['rule','proof','other']);
        validateFormula(p.other);
        const a=visit(p.proof,depth+1);
        return {conclusion:['or',p.other,a.conclusion],context:a.context};
      }
      default: throw new Error('unknown inference rule');
    }
  }
  return visit(proof,0);
}
function checkBound(proof, expectedConclusion, expectedContext) {
  const budget={nodes:0};
  validateFormula(expectedConclusion,0,budget);
  if (!Array.isArray(expectedContext)) throw new Error('expected context must be an array');
  expectedContext.forEach(f=>validateFormula(f,0,budget));
  const result=check(proof,budget);
  if (!eq(result.conclusion,expectedConclusion)) throw new Error('claim conclusion mismatch');
  const canon=xs=>xs.map(x=>JSON.stringify(x)).sort();
  if (!eq(canon(result.context),canon(expectedContext))) throw new Error('assumption context mismatch');
  return result;
}
function atoms(formula,out=new Set(),budget={nodes:0}) {
  validateFormula(formula,0,budget);
  function walk(f){if(typeof f==='string')out.add(f);else {walk(f[1]);walk(f[2]);}}
  walk(formula);
  return out;
}
function evalF(formula,env,steps={count:0}) {
  validateFormula(formula);
  function tick(){if(++steps.count>MAX_EVAL_STEPS)throw new Error('truth-table evaluation budget exceeded');}
  function tick(){if(++steps.count>MAX_EVAL_STEPS)throw new Error('truth-table evaluation budget exceeded');}
  function walk(f) {
    tick();
    if(typeof f==='string') return !!env[f];
    const [op,a,b]=f;
    if(op==='and') return walk(a)&&walk(b);
    if(op==='or') return walk(a)||walk(b);
    if(op==='imp') return !walk(a)||walk(b);
    throw new Error('unknown formula operator');
  }
  return walk(formula);
}
function tautologyUnderContext(conclusion,context) {
  const inputBudget={nodes:0};
  validateFormula(conclusion,0,inputBudget);
  if(!Array.isArray(context)) throw new Error('context must be an array');
  for(const f of context) validateFormula(f,0,inputBudget);
  const names=[...new Set([...atoms(conclusion,new Set(),inputBudget),...context.flatMap(f=>[...atoms(f,new Set(),inputBudget)])])];
  if(names.length>MAX_ATOMS) throw new Error('truth-table atom limit exceeded');
  const steps={count:0};
  for(let mask=0;mask<(1<<names.length);mask++){
    const env=Object.fromEntries(names.map((n,i)=>[n,!!(mask&(1<<i))]));
    if(context.every(f=>evalF(f,env,steps))&&!evalF(conclusion,env,steps)) return false;
  }
  return true;
}
module.exports={MAX_DEPTH,MAX_NODES,MAX_ATOMS,MAX_EVAL_STEPS,validateFormula,check,checkBound,eq,evalF,tautologyUnderContext};
