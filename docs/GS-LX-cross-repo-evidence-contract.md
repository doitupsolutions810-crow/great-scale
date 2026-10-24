# GS-LX: Cross-Repo Evidence Contract

**Status:** DRAFT — research note, not yet executed
**Date:** 2026-10-24
**Repos spanned:** CycleKernal, great-scale, living-intermediate-control-plane
**Lineage:** XC → XCVII → GS-LVI → GS-LVII → GS-LX

---

## 1. The Problem

Six independent PRs across three repos rediscovered the same architecture without referencing each other:

| PR | Repo | What it built |
|----|------|---------------|
| #10 | CycleKernal | System 24: Provenance-Conditioned Projection — projected score as observation, companion channel states attribution, margins, provenance |
| #9 | CycleKernal | Signed eta, channel gap, ratio, four threshold margins, SHA-256 fusion-state fingerprint, explicit non-finite rejection |
| #118 | great-scale | Two loss-envelope families, both strictly positive third derivative, Hermite majorant proved sharp for fixed moments, chord fallback labeled NOT_CERTIFIED |
| #113 | great-scale | Two-gate structure: structural identifiability first, then robust identifiability under bounded error ε, separation margin d − 2ε as certified quantity |
| #16 | living-intermediate | Self-hosted ephemeral runner bootstrap, cone-floor correction φ³ → φ² |
| #15 | living-intermediate | Fail-closed CycleKernal client with source-blob pinning, 42 passing self-tests |

Each arrived at the witness-alongside-scalar discipline from its own angle. That convergence is the signal: the principle is load-bearing.

But the schemas don't interoperate. CycleKernal's companion v1, great-scale's loss-envelope v1, and the fusion-state v2 fingerprint are three dialects of one language.

## 2. The Contract

### 2.1 Core Invariant

**No scalar may be emitted without its companion channel.**

A scalar without a companion is ESTIMATE. A scalar with a companion is SHARP_CERTIFICATE. The system must never act on ESTIMATE as if it were SHARP_CERTIFICATE.

### 2.2 Evidence Record Schema (v1.0)

```json
{
  "schema_version": "gs-lx/1.0",
  "record_id": "<sha256 of canonical JSON>",
  "timestamp": "<ISO-8601>",
  "repo": "<repo-name>",
  "commit_sha": "<full SHA>",
  "branch": "<branch-name>",
  "descent_id": "<e.g. XCVIII, GS-LVI>",
  "channels": {
    "primary": { "name": "<scalar name>", "value": "<number>", "unit": "<string>" },
    "companion": { "name": "<condition name>", "value": "<declared condition>", "provenance": "<source>" }
  },
  "margins": {
    "separation": "<d - 2ε or equivalent>",
    "threshold_distances": { "<gate>": "<distance>" }
  },
  "error_bound": { "epsilon": "<number>", "source": "<bounded-error model>" },
  "grade": "SHARP_CERTIFICATE | ESTIMATE | FALLBACK | NOT_CERTIFIED",
  "execution_receipt": {
    "runner_id": "<nonzero or ZERO>",
    "steps_executed": "<count>",
    "log_retrievable": "<bool>",
    "sha_match": "<bool>"
  }
}
```

### 2.3 Grade Semantics

- **SHARP_CERTIFICATE:** companion channel emitted, error bound stated, execution receipt nonzero.
- **ESTIMATE:** scalar emitted, companion absent or partial.
- **FALLBACK:** companion explicitly declared missing; system must not act.
- **NOT_CERTIFIED:** explicitly labeled as such (e.g., chord fallback in #118).

### 2.4 Cross-Repo Binding

All three repos emit records in this schema. A GS-LX aggregator (future) merges records across repos by `commit_sha` and `descent_id`, producing a unified Ψ ledger:

Ψ = H − σ

where H is the full evidence tuple (channels, margins, provenance, proof status, error bound, execution receipt) and σ is any projection that discards a channel.

## 3. Mapping to Existing Work

| Existing artifact | GS-LX role |
|-------------------|------------|
| CycleKernal companion v1 (#9, #10) | Primary channel dialect — maps to `channels.primary` + `channels.companion` |
| great-scale loss-envelope v1 (#118) | Margin dialect — maps to `margins` + `error_bound` |
| Fusion-state v2 fingerprint (#9) | Provenance dialect — maps to `channels.companion.provenance` + `record_id` |
| PR #16 runner bootstrap | Execution surface — maps to `execution_receipt` |
| PR #15 fail-closed client | Verification consumer — reads records, refuses ESTIMATE-as-SHARP |

## 4. Testable Predictions

1. **Fiber constancy:** For any quotient-circle contraction, C(x) = C(x + 9n) for all integer n. The seam pair (0, 9) must produce identical outputs. GS-LVI seam tests in great-scale and CycleKernal already encode this.

2. **Demotion reachability:** apply_fusion must pass the raw promoted boolean, not `promoted ∧ score ≥ PROMOTE_THRESHOLD`. The demote branch must be reachable for any colony below DEMOTE_THRESHOLD. Fixed in CycleKernal efb1d08.

3. **Identity non-collision:** sha256(user_id)[:12] must be distinct for distinct user_ids. The six-char slice collides (alice123 vs alice199). Fixed in CycleKernal 4a4ef074 and TrainLLM.

4. **Execution nonzero:** No CI run may emit a failure receipt with runner_id = 0. This is currently violated across 1,159+ great-scale runs and 9+ CycleKernal runs. Open support ticket.

5. **Grade honesty:** No ESTIMATE may be labeled SHARP_CERTIFICATE. hypothesisReport's "supports" label for residuals < 0.5 at the fixed point is a grade violation — fixed direction in living-intermediate GS-LVI bridge work.

## 5. The Profound Finding

A system that emits numbers without emitting the conditions under which those numbers are valid will eventually act on the shadow as if it were the object.

This is not a software bug class. It is the load-bearing failure mode of any certificate-based control plane, and it is identical in shape to the non-identifiability the Great Scale was built to name.

Ψ = H − σ only means something when σ's shadow is named alongside it.

The three repos have each independently discovered this. GS-LX is the act of naming it once, across all of them, in one schema.

## 6. Next Descent: GS-LXI

Unify the three dialects into a single runtime library (one npm package, one pip package) that all three repos import. The contract becomes executable, not documentary. The companion channel becomes a type, not a comment.

---

*GS-LX drafted 2026-10-24. Not yet executed. Companion channel: this note itself.*