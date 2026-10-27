import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { validateRepositoryMap } from "./tools/validate-repository-map.mjs";

const baseline = JSON.parse(readFileSync(new URL("./integration/repository-map.json", import.meta.url), "utf8"));

function edgeProof(overrides = {}) {
  const testCommitSha = "c".repeat(40);
  const testRunUrl = "https://github.com/doitupsolutions810-crow/great-scale/actions/runs/123456";
  return {
    sourceRepository: "great-scale",
    targetRepository: "living-intermediate-control-plane",
    sourceCommitSha: "a".repeat(40),
    targetCommitSha: "b".repeat(40),
    testRepository: "great-scale",
    testCommitSha,
    testRunHeadSha: testCommitSha,
    testRunId: 123456,
    testRunAttempt: 1,
    testRunConclusion: "success",
    testRunUrl,
    observedResult: "pass",
    evidenceUrl: testRunUrl + "/artifacts/789",
    ...overrides,
  };
}

function repositoryProof(overrides = {}) {
  const testCommitSha = "c".repeat(40);
  const testRunUrl = "https://github.com/doitupsolutions810-crow/great-scale/actions/runs/123456";
  return {
    subjectRepository: "UnifiedToolStackApplication-utsp-platform",
    commitSha: "a".repeat(40),
    testRepository: "great-scale",
    testCommitSha,
    testRunHeadSha: testCommitSha,
    testRunId: 123456,
    testRunAttempt: 1,
    testRunConclusion: "success",
    testRunUrl,
    observedResult: "pass",
    evidenceUrl: testRunUrl + "/artifacts/789",
    ...overrides,
  };
}

test("public-only repository snapshot is valid and does not claim runtime verification", () => {
  assert.equal(baseline.scope, "public-only");
  assert.equal(baseline.repositories.length, 14);
  assert.equal(baseline.repositories.length, baseline.expectedRepositoryCount);
  assert.equal(baseline.interfaces.length, 5);
  assert.ok(baseline.repositories.every((repo) => repo.integrationStatus === "not-end-to-end-verified"));
  assert.ok(baseline.interfaces.every((edge) => edge.verificationStatus === "proposed-not-verified"));
  assert.deepEqual(validateRepositoryMap(baseline), []);
});

test("duplicate repositories are rejected", () => {
  const candidate = structuredClone(baseline);
  candidate.repositories.push(structuredClone(candidate.repositories[0]));
  assert.ok(validateRepositoryMap(candidate).some((message) => message.startsWith("duplicate repository name:")));
});

test("unknown interface endpoints are rejected", () => {
  const candidate = structuredClone(baseline);
  candidate.interfaces[0].to = "repository-that-does-not-exist";
  assert.ok(validateRepositoryMap(candidate).some((message) => message.includes("unknown repository")));
});

test("inventory count drift is rejected until the snapshot is explicitly updated", () => {
  const candidate = structuredClone(baseline);
  candidate.expectedRepositoryCount += 1;
  assert.ok(validateRepositoryMap(candidate).some((message) => message.includes("repository count mismatch")));
});

test("a repository cannot be marked verified without exact-run execution evidence", () => {
  const candidate = structuredClone(baseline);
  candidate.repositories[0].integrationStatus = "verified";
  assert.ok(validateRepositoryMap(candidate).some((message) => message.includes("complete exact-run proof object")));
});

test("an interface cannot be marked verified without both endpoint revisions and execution proof", () => {
  const candidate = structuredClone(baseline);
  candidate.interfaces[0].verificationStatus = "verified";
  assert.ok(validateRepositoryMap(candidate).some((message) => message.includes("complete exact-run proof object")));
});

test("a fully bound successful run can support a repository verification claim", () => {
  const candidate = structuredClone(baseline);
  candidate.repositories[0].integrationStatus = "verified";
  candidate.repositories[0].verification = repositoryProof();
  assert.deepEqual(validateRepositoryMap(candidate), []);
});

test("a fully bound successful run can support an interface verification claim", () => {
  const candidate = structuredClone(baseline);
  candidate.interfaces[0].verificationStatus = "verified";
  candidate.interfaces[0].verification = edgeProof();
  assert.deepEqual(validateRepositoryMap(candidate), []);
});

test("an interface cannot be promoted on a failed or inexact-head run", () => {
  const failed = structuredClone(baseline);
  failed.interfaces[0].verificationStatus = "verified";
  failed.interfaces[0].verification = edgeProof({ testRunConclusion: "failure" });
  assert.ok(validateRepositoryMap(failed).some((message) => message.includes("testRunConclusion must equal success")));

  const staleHead = structuredClone(baseline);
  staleHead.interfaces[0].verificationStatus = "verified";
  staleHead.interfaces[0].verification = edgeProof({ testRunHeadSha: "d".repeat(40) });
  assert.ok(validateRepositoryMap(staleHead).some((message) => message.includes("testRunHeadSha must equal testCommitSha")));
});

test("an interface cannot omit either endpoint revision", () => {
  const candidate = structuredClone(baseline);
  candidate.interfaces[0].verificationStatus = "verified";
  const proof = edgeProof();
  delete proof.targetCommitSha;
  candidate.interfaces[0].verification = proof;
  assert.ok(validateRepositoryMap(candidate).some((message) => message.includes("targetCommitSha must be a full 40-character SHA")));
});

test("verification proof cannot be replayed onto a different repository edge", () => {
  const wrongRepository = structuredClone(baseline);
  wrongRepository.interfaces[0].verificationStatus = "verified";
  wrongRepository.interfaces[0].verification = edgeProof({ sourceRepository: "CycleKernal" });
  assert.ok(validateRepositoryMap(wrongRepository).some((message) => message.includes("sourceRepository must equal edge.from")));

  const wrongSubject = structuredClone(baseline);
  wrongSubject.repositories[0].integrationStatus = "verified";
  wrongSubject.repositories[0].verification = repositoryProof({ subjectRepository: "CycleKernal" });
  assert.ok(validateRepositoryMap(wrongSubject).some((message) => message.includes("subjectRepository must equal")));
});

test("test run and evidence URLs are bound to a registered repository and exact run", () => {
  const candidate = structuredClone(baseline);
  candidate.interfaces[0].verificationStatus = "verified";
  candidate.interfaces[0].verification = edgeProof({
    testRunUrl: "https://github.com/doitupsolutions810-crow/another-repo/actions/runs/123456"
  });
  assert.ok(validateRepositoryMap(candidate).some((message) => message.includes("testRunUrl must bind the registered test repository and run ID")));

  const badEvidence = structuredClone(baseline);
  badEvidence.interfaces[0].verificationStatus = "verified";
  badEvidence.interfaces[0].verification = edgeProof({
    evidenceUrl: "https://github.com/doitupsolutions810-crow/great-scale/actions/runs/999999/artifacts/789"
  });
  assert.ok(validateRepositoryMap(badEvidence).some((message) => message.includes("evidenceUrl must be a durable URL within the exact test run")));
});

test("registry binds the shared operation evidence contract and its schema", () => {
  const candidate = structuredClone(baseline);
  candidate.operationEvidenceContract.version = "v99";
  assert.ok(validateRepositoryMap(candidate).some((message) => message.includes("operationEvidenceContract")));
  const missingSchema = structuredClone(baseline);
  delete missingSchema.operationEvidenceContract.schemaPath;
  assert.ok(validateRepositoryMap(missingSchema).some((message) => message.includes("operationEvidenceContract")));
  const missing = structuredClone(baseline);
  delete missing.operationEvidenceContract;
  assert.ok(validateRepositoryMap(missing).some((message) => message.includes("operationEvidenceContract")));
});

test("public-only registry rejects a private repository record", () => {
  const candidate = structuredClone(baseline);
  candidate.repositories[0].visibility = "private";
  assert.ok(validateRepositoryMap(candidate).some((message) => message.includes("public-only registry")));
});

test("Great Scale to control-plane edge requires a live build-bound G6 residual and stays unverified", () => {
  const edge = baseline.interfaces.find(item =>
    item.from === "great-scale" && item.to === "living-intermediate-control-plane"
  );
  assert.ok(edge);
  assert.equal(edge.verificationStatus, "proposed-not-verified");
  assert.match(edge.contract, /not a live production measurement endpoint/);
  for (const requirement of [
    "live-measurement-source-identity",
    "same-build-and-immutable-artifact-digest",
    "source-issued-measured-at-freshness",
    "finite-residual-value-and-cone-policy",
    "no-default-zero-or-caller-supplied-value-as-observation",
    "authoritative-g0-g6-producer-verification",
    "independent-signing-key-and-pinned-trust-anchor",
    "exact-head-end-to-end-test-run",
  ]) {
    assert.ok(edge.requiredEvidence.includes(requirement), `missing G6 promotion evidence: ${requirement}`);
  }
});
