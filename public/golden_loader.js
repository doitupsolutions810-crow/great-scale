/**
 * Golden-vector loader: great-scale verifies itself.
 * Reads tests/fixtures/golden_vectors.json and asserts parity against
 * residual.cjs exports. Fails on any drift. Closes the bootstrap gap:
 * the measuring instrument checks its own measurements without Avrone.
 */
import { createRequire } from 'module';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { join,dirname } from 'path';

const require = createRequire(import.meta.url);
const __dirname =dirname(fileURLToPath(import.meta.url));

// residual.cjs is CJS; load via require
const residual = require(join(__dirname, 'residual.cjs'));

const vectors = JSON.parse(
  readFileSync(join(__dirname, '..', 'tests', 'fixtures', 'golden_vectors.json'), 'utf8')
);

const TOL = 1e-12;
const fails = [];
function check(cond, msg) { if (!cond) fails.push(msg); }

// heat === Bernoulli variance
for (const row of vectors.heat) {
  check(Math.abs(row.S - row.h * (1 - row.h)) <= TOL, `heat S mismatch at h=${row.h}`);
}

// psi === cone + S
for (const row of vectors.psi) {
  check(Math.abs(row.psi - (vectors.meta.cone + row.S)) <= TOL, `psi mismatch at S=${row.S}`);
}

// cascade lambda === phi^-n
const phi = vectors.meta.phi;
for (const row of vectors.cascade_lambda) {
  check(Math.abs(row.lambda - Math.pow(phi, -row.n)) <= TOL, `cascade lambda mismatch at n=${row.n}`);
}

// topological saturation
for (const row of vectors.topological_saturation) {
  const t = row.tau;
  const S = (1 - t * t) / 4;
  const n = 8 - (1 - t * t);
  check(Math.abs(row.S - S) <= TOL, `topo S mismatch at tau=${t}`);
  check(Math.abs(row.n - n) <= TOL, `topo n mismatch at tau=${t}`);
  check(Math.abs(row.lambda - Math.pow(phi, -n)) <= TOL, `topo lambda mismatch at tau=${t}`);
  check(Math.abs(row.logCoord - (1 - t * t)) <= TOL, `topo logCoord mismatch at tau=${t}`);
  check(Math.abs(row.psi - (vectors.meta.cone + S)) <= TOL, `topo psi mismatch at tau=${t}`);
}

// soft contract: FIXED + 0.5 * (((x%9)+9)%9 - FIXED), fixed point at 4.5
function soft(x) {
  const r = ((x % 9) + 9) % 9;
  return vectors.meta.fixed_point + 0.5 * (r - vectors.meta.fixed_point);
}
for (const row of vectors.soft_contract) {
  check(Math.abs(row.out - soft(row.x)) <= TOL, `softContract mismatch at x=${row.x}`);
}
check(soft(4.5) === 4.5, 'softContract fixed point is not 4.5');

// residual count: n === 8 - 4S
for (const row of vectors.residual_count) {
  check(Math.abs(row.n - (8 - 4 * row.S)) <= TOL, `residualCount mismatch at S=${row.S}`);
}

// evidence channel
for (const row of vectors.evidence_channel) {
  check(Math.abs(row.S - row.p * (1 - row.p)) <= TOL, `evidence S mismatch at p=${row.p}`);
  if (row.p === 0) check(row.orientation === 'pass', `p=0 orientation should be pass`);
  if (row.p === 1) check(row.orientation === 'fail', `p=1 orientation should be fail`);
  if (row.p > 0 && row.p < 1) check(row.orientation === 'mixed', `0<p<1 orientation should be mixed at p=${row.p}`);
  check(row.onConeFloor === (row.S === 0), `onConeFloor mismatch at p=${row.p}`);
  if (row.p > 0 && row.runsFor95 != null) {
    const n95 = Math.ceil(Math.log(0.05) / Math.log(1 - row.p));
    check(row.runsFor95 === n95, `runsFor95 mismatch at p=${row.p}: got ${row.runsFor95}, want ${n95}`);
  }
}

// orientation blindness: heat(p) === heat(1-p)
for (const row of vectors.heat) {
  const twin = vectors.heat.find(r => Math.abs(r.h - (1 - row.h)) <= TOL);
  check(twin && Math.abs(twin.S - row.S) <= TOL, `orientation blindness broken at h=${row.h}`);
}

// cone meta
check(Math.abs(vectors.meta.cone - Math.pow(phi, -2)) <= TOL, 'cone meta != phi^-2');
check(vectors.meta.residual_partition.reduce((a, b) => a + b, 0) === 8, 'partition must sum to 8');

if (fails.length) {
  console.error('GOLDEN LOADER FAIL (' + fails.length + '):' + fails.map(f => '\n  - ' + f).join(''));
  process.exit(1);
}
console.log('GOLDEN LOADER PASS: ' + (vectors.heat.length + vectors.psi.length + vectors.cascade_lambda.length + vectors.topological_saturation.length + vectors.soft_contract.length + vectors.residual_count.length + vectors.evidence_channel.length) + ' vectors verified against residual.cjs'');
