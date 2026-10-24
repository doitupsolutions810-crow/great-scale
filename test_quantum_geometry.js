const assert = require('assert');
const { CONE, heat } = require('./public/scale.cjs');
const { quantumGeometryBridge } = require('./public/quantum-geometry.cjs');
let passed = 0, failed = 0;
function test(name, fn) { try { fn(); passed++; console.log('  PASS  ' + name); } catch (e) { failed++; console.log('  FAIL  ' + name + ' — ' + e.message); } }
function close(a, b, t = 1e-10) { assert.ok(Math.abs(a - b) <= t, a + ' != ' + b); }

test('zero curvature maps to maximum heat', () => {
 const r=quantumGeometryBridge({g11:1,g12:0,g22:1,curvature:0});
 close(r.curvatureFraction,0); close(r.hQuantum,.5); close(r.SQuantum,.25); close(r.SQuantum,heat(r.hQuantum)); close(r.relativeResidual,1); close(r.psiQuantum,CONE+.25);
});
test('saturation maps to zero heat and cone floor', () => {
 const r=quantumGeometryBridge({g11:1,g12:0,g22:1,curvature:2});
 close(r.curvatureFraction,1); close(r.hQuantum,1); close(r.SQuantum,0); close(r.relativeResidual,0); close(r.detQ,0); close(r.psiQuantum,CONE);
});
test('intermediate curvature encodes normalized residual', () => {
 const r=quantumGeometryBridge({g11:1,g12:0,g22:1,curvature:1});
 close(r.curvatureFraction,.5); close(r.detQ,.75); close(r.relativeResidual,.75); close(r.SQuantum,.1875); close(r.SQuantum,r.relativeResidual/4); close(r.psiQuantum,CONE+r.SQuantum);
});
test('normalized map invariant under common metric-curvature scaling', () => {
 const a=quantumGeometryBridge({g11:1,g12:0,g22:1,curvature:1}),b=quantumGeometryBridge({g11:4,g12:0,g22:4,curvature:4});
 close(a.curvatureFraction,b.curvatureFraction); close(a.SQuantum,b.SQuantum);
});
test('qutrit zero-curvature family retains metric area', () => {
 const x=.3,y=.4,s=1+x*x+y*y,g11=(1+y*y)/(s*s),g12=-x*y/(s*s),g22=(1+x*x)/(s*s);
 const r=quantumGeometryBridge({g11,g12,g22,curvature:0});
 close(r.detG,1/(s*s*s)); close(r.detQ,r.detG); close(r.relativeResidual,1); close(r.SQuantum,.25);
});
test('scalar heat discards curvature sign but diagnostic preserves it', () => {
 const a=quantumGeometryBridge({g11:1,g12:0,g22:1,curvature:1}),b=quantumGeometryBridge({g11:1,g12:0,g22:1,curvature:-1});
 close(a.curvatureFraction,b.curvatureFraction); close(a.SQuantum,b.SQuantum); close(a.signedCurvature,1); close(b.signedCurvature,-1);
});
test('metric eigenvalues preserve anisotropy at equal determinant', () => {
 const a=quantumGeometryBridge({g11:1,g12:0,g22:1,curvature:0}),b=quantumGeometryBridge({g11:4,g12:0,g22:.25,curvature:0});
 close(a.detG,1); close(b.detG,1); close(a.SQuantum,b.SQuantum); close(a.metricAnisotropy,1); close(b.metricAnisotropy,.0625); close(b.metricEigenvalues[0],.25); close(b.metricEigenvalues[1],4);
});
test('pure-qubit Bloch sphere saturates QGT bound at regular points', () => {
 const t=.7,r=quantumGeometryBridge({g11:.25,g12:0,g22:Math.sin(t)**2/4,curvature:Math.sin(t)/2});
 close(r.detG,Math.sin(t)**2/16); close(r.detQ,0,1e-12); close(r.curvatureFraction,1); close(r.SQuantum,0); close(r.psiQuantum,CONE);
});
test('rejects QGT positivity violation', () => assert.throws(()=>quantumGeometryBridge({g11:1,g12:0,g22:1,curvature:2.01}),/QGT positivity violated/));
test('rejects degenerate metric', () => assert.throws(()=>quantumGeometryBridge({g11:1,g12:1,g22:1,curvature:0}),/positive and nondegenerate/));
test('rejects negative-definite metric', () => assert.throws(()=>quantumGeometryBridge({g11:-1,g12:0,g22:-1,curvature:0}),/diagonal entries must be positive/));
test('rejects zero diagonal metric', () => assert.throws(()=>quantumGeometryBridge({g11:0,g12:0,g22:1,curvature:0}),/diagonal entries must be positive/));

test('bridge scalar is invariant at extreme common scales and avoids determinant underflow', () => {
 const base=quantumGeometryBridge({g11:1,g12:0,g22:1,curvature:1});
 const tiny=quantumGeometryBridge({g11:1e-200,g12:0,g22:1e-200,curvature:1e-200});
 close(tiny.curvatureFraction,base.curvatureFraction); close(tiny.SQuantum,base.SQuantum);
 assert.ok(tiny.metricEigenvalues.every(Number.isFinite)); close(tiny.metricEigenvalues[0]/1e-200,1); close(tiny.metricEigenvalues[1]/1e-200,1);
 const huge=quantumGeometryBridge({g11:1e200,g12:0,g22:1e200,curvature:1e200});
 close(huge.curvatureFraction,base.curvatureFraction); close(huge.SQuantum,base.SQuantum);
 assert.ok(huge.metricEigenvalues.every(Number.isFinite)); close(huge.metricEigenvalues[0]/1e200,1); close(huge.metricEigenvalues[1]/1e200,1);
});
console.log('\nquantum geometry bridge tests: '+passed+' passed, '+failed+' failed');
process.exit(failed?1:0);
