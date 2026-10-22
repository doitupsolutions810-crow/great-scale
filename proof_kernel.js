'use strict';
// Minimal natural-deduction checker for propositional logic.
// This is an educational reference kernel, not a production proof assistant.
const eq = (a,b) => JSON.stringify(a) === JSON.stringify(b);
const union = (a,b) => [...a, ...b];
function check(p) {
  if (!p || typeof p !== 'object') throw new Error('malformed proof');
  switch (p.rule) {
    case 'assume':
      if (!p.formula) throw new Error('missing assumption formula');
      return { conclusion:p.formula, context:[p.formula] };
    case 'andI': {
      const a=check(p.left), b=check(p.right);
      return { conclusion:['and',a.conclusion,b.conclusion], context:union(a.context,b.context) };
    }
    case 'andEL': {
      const a=check(p.proof);
      if (a.conclusion?.[0] !== 'and') throw new Error('andEL requires conjunction');
      return { conclusion:a.conclusion[1], context:a.context };
    }
    case 'andER': {
      const a=check(p.proof);
      if (a.conclusion?.[0] !== 'and') throw new Error('andER requires conjunction');
      return { conclusion:a.conclusion[2], context:a.context };
    }
    case 'impI': {
      const a=check(p.proof);
      const i=a.context.findIndex(x=>eq(x,p.assumption));
      if (i<0) throw new Error('impI assumption not present for discharge');
      const ctx=[...a.context]; ctx.splice(i,1);
      return { conclusion:['imp',p.assumption,a.conclusion], context:ctx };
    }
    case 'impE': {
      const a=check(p.function), b=check(p.argument);
      if (a.conclusion?.[0] !== 'imp' || !eq(a.conclusion[1],b.conclusion)) throw new Error('impE antecedent mismatch');
      return { conclusion:a.conclusion[2], context:union(a.context,b.context) };
    }
    case 'orIL': {
      const a=check(p.proof);
      return { conclusion:['or',a.conclusion,p.other], context:a.context };
    }
    case 'orIR': {
      const a=check(p.proof);
      return { conclusion:['or',p.other,a.conclusion], context:a.context };
    }
    default: throw new Error('unknown inference rule');
  }
}
function atoms(f, out=new Set()) {
  if (typeof f==='string') out.add(f);
  else if (Array.isArray(f)) f.slice(1).forEach(x=>atoms(x,out));
  return out;
}
function evalF(f, env) {
  if (typeof f==='string') return !!env[f];
  const [op,a,b]=f;
  if(op==='and') return evalF(a,env)&&evalF(b,env);
  if(op==='or') return evalF(a,env)||evalF(b,env);
  if(op==='imp') return !evalF(a,env)||evalF(b,env);
  throw new Error('unknown formula operator');
}
function tautologyUnderContext(conclusion, context) {
  const all=new Set([...atoms(conclusion),...context.flatMap(f=>[...atoms(f)])]);
  const names=[...all];
  for(let mask=0;mask<(1<<names.length);mask++){
    const env=Object.fromEntries(names.map((n,i)=>[n,!!(mask&(1<<i))]));
    if(context.every(f=>evalF(f,env))&&!evalF(conclusion,env)) return false;
  }
  return true;
}
module.exports={check,eq,evalF,tautologyUnderContext};
