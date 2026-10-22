'use strict';
// Hardened educational reference kernel. Not production-certified.
const MAX_DEPTH = 256;
const MAX_NODES = 10000;
const MAX_ATOMS = 16;
const eq = (a,b) => JSON.stringify(a) === JSON.stringify(b);
const union = (a,b) => [...a,...b];

function validateFormula(formula, depth=0, budget={nodes:0}) {
  if (depth > MAX_DEPTH) throw new Error('formula depth limit exceeded');
  if (++budget.nodes > MAX_NODES) throw new Error('formula node limit exceeded');
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
function check(proof) {
  const budget={nodes:0};
  function visit(p,depth) {
    if (depth > MAX_DEPTH) throw new Error('proof depth limit exceeded');
    if (++budget.nodes > MAX_NODES) throw new Error('proof node limit exceeded');
    if (!p || typeof p !== 'object' || Array.isArray(p)) throw new Error('malformed proof');
    const keys=Object.keys(p).sort();
    const requireKeys=(expected) => {
      if (JSON.stringify(keys) !== JSON.stringify([...expected].sort())) throw new Error('proof fields do not match rule schema');
    };
    if (typeof p.rule !== 'string') throw new Error('missing proof rule');
    switch(p.rule) {
      case 'assume':
        requireKeys(['rule','formula']);
        validateFormula(p.formula);
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
        validateFormula(p.assumption);
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
        validateFormula(p.other);
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
  validateFormula(expectedConclusion);
  if (!Array.isArray(expectedContext)) throw new Error('expected context must be an array');
  expectedContext.forEach(f=>validateFormula(f));
  const result=check(proof);
  if (!eq(result.conclusion,expectedConclusion)) throw new Error('claim conclusion mismatch');
  const canon=xs=>xs.map(x=>JSON.stringify(x)).sort();
  if (!eq(canon(result.context),canon(expectedContext))) throw new Error('assumption context mismatch');
  return result;
}
function atoms(formula,out=new Set()) {
  validateFormula(formula);
  function walk(f){if(typeof f==='string')out.add(f);else {walk(f[1]);walk(f[2]);}}
  walk(formula);
  return out;
}
function evalF(formula,env) {
  validateFormula(formula);
  function walk(f) {
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
  validateFormula(conclusion);
  if(!Array.isArray(context)) throw new Error('context must be an array');
  for(const f of context) validateFormula(f);
  const names=[...new Set([...atoms(conclusion),...context.flatMap(f=>[...atoms(f)])])];
  if(names.length>MAX_ATOMS) throw new Error('truth-table atom limit exceeded');
  for(let mask=0;mask<(1<<names.length);mask++){
    const env=Object.fromEntries(names.map((n,i)=>[n,!!(mask&(1<<i))]));
    if(context.every(f=>evalF(f,env))&&!evalF(conclusion,env)) return false;
  }
  return true;
}
module.exports={MAX_DEPTH,MAX_NODES,MAX_ATOMS,validateFormula,check,checkBound,eq,evalF,tautologyUnderContext};
