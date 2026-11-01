'use strict';
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const html = fs.readFileSync(path.join(__dirname, 'public', 'atlas.html'), 'utf8');
const checks = [
  ['six map choices exist', ['reflect','contract','involution','heat','mean','compose'].every((id) => html.includes('value="' + id + '"'))],
  ['interactive quotient seam view exists', html.includes('value="seam"') && html.includes('Quotient seam audit')],
  ['rotation and zoom interactions exist', html.includes("pointerdown") && html.includes("addEventListener('wheel'")],
  ['four role council exists', ['Algebraist','Topologist','Numerical Analyst','Skeptic / Falsifier'].every((s) => html.includes(s))],
  ['debate modes exist', ['balanced','hostile','proof'].every((s) => html.includes('data-mode="' + s + '"'))],
  ['session export exists', html.includes('great-scale-atlas-session.json') && html.includes('JSON.stringify')],
  ['local-only LLM boundary is explicit', html.includes('Not a live LLM run') || html.includes('not a live external LLM responses')),
  ['evidence and authority are separated', html.includes('Model output ≠ empirical proof ≠ production authorization.')],
  ['public research UI excludes private Control12 repo name', !html.includes('control12-lattice-ops')],
  ['accessible canvas label exists', html.includes('aria-label="Interactive endomorphism geometry plot"')]
];
for (const [name, ok] of checks) {
  assert.equal(ok, true, name);
  process.stdout.write('PASS ' + name + '\n');
}
process.stdout.write(checks.length + '/' + checks.length + ' atlas contract checks passed\n');
