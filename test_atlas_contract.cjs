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
  ['local-only LLM boundary is explicit', html.includes('Not a live LLM run') || html.includes('not a live external LLM responses')],
  ['evidence and authority are separated', html.includes('Model output ≠ empirical proof ≠ production authorization.')],
  ['public research UI excludes private Control12 repo name', !html.includes('control12-lattice-ops')],
  ['accessible canvas label exists', html.includes('aria-label="Interactive endomorphism geometry plot"')],
  ['live AVRONE bridge panel exists', html.includes('id="liveBridge"') && html.includes('id="liveRunBtn"')],
  ['live bridge pins a full commit and sends no browser token', html.includes('commit_sha:$(') && html.includes("fetch('/api/research/debate'") && !html.includes('localStorage.setItem(\'avrone-admin-token\'')],
  ['receipt is surfaced as an explicit verification boundary', html.includes('result_digest_sha256') && html.includes('evidence_digest_sha256') && html.includes('agent conclusions remain unverified')],
  ['stored receipt retrieval uses same-origin credentials', html.includes('credentials:\'same-origin\'') && html.includes('/api/research/receipts/') === false]
];
for (const [name, ok] of checks) {
  assert.equal(ok, true, name);
  process.stdout.write('PASS ' + name + '\n');
}
process.stdout.write(checks.length + '/' + checks.length + ' atlas contract checks passed\n');
