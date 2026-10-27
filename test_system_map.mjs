import test from "node:test";
import { createHash } from "node:crypto";
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
    "target-build-and-target-artifact-digest-binding",
    "source-issued-measured-at-freshness",
    "finite-residual-value-and-cone-policy",
    "topology-derived-residual-domain-0-to-0.25",
    "approved-independent-numerical-certificate-method",
    "certificate-source-commit-and-model-input-digest-match",
    "certificate-proof-artifact-digest-verified",
    "certified-curvature-and-metric-area-error-bounds-within-tolerance",
    "empirical-richardson-estimates-not-treated-as-rigorous",
    "numerical-certifier-identity-pinned-independent-of-receipt",
    "no-default-zero-or-caller-supplied-value-as-observation",
    "authoritative-g0-g6-producer-verification",
    "independent-signing-key-and-pinned-trust-anchor",
    "exact-head-end-to-end-test-run",
    "versioned-g6-residual-measurement-schema-v1",
    "measurement-st-topological-maps-to-consumer-residual-S",
    "measurement-timestamp-maps-to-consumer-residual-measured-at",
    "issuer-and-target-build-id-map-to-residual-provenance",
    "source-commit-equals-successful-run-head-sha",
    "canonical-json-sha256-and-ed25519-signature-verified",
    "model-parameter-and-input-digest-reproduced",
    "numerical-convergence-and-rigorous-error-bounds-validated",
    "topological-mapping-valid-true",
    "measurement-artifact-distinct-from-target-artifact",
    "measurement-build-id-distinct-from-target-build-id",
    "target-build-id-matches-g0-g6-attestation-build-id",
    "target-artifact-digest-matches-g0-g6-attestation-artifact-digest",
    "quadrature-rigorous-certificate-distinct-from-empirical-estimates",
    "numerical-certificate-upper-bounds-and-proof-digest-verified",
    "numerical-certificate-source-commit-and-model-input-digest-bound",
    "independent-numerical-certificate-verified",
    "target-commit-matches-g0-g6-attestation-source-commit",
    "both-source-model-commit-and-consumer-release-commit-pinned",
  ]) {
    assert.ok(edge.requiredEvidence.includes(requirement), `missing G6 promotion evidence: ${requirement}`);
  }
});


test("registry pins the schema-only G6 measurement receipt and exact consumer mapping", () => {
  const contract = baseline.g6ResidualMeasurementContract;
  assert.deepEqual(contract, {
    repository: "great-scale",
    path: "contracts/g6-residual-measurement/v1.schema.json",
    schemaBlobSha: "89ed8276ea7ba4d65fa9b416a960ad5acba296d2",
    version: "v1",
    status: "schema-only-not-producer",
    mapping: {
      measurementSTopologicalToResidualS: "measurement.STopological -> residual.S",
      measuredAtToResidualMeasuredAt: "measuredAt -> residual.measuredAt",
      issuerToResidualSourceId: "issuer -> residual.sourceId",
      measurementBuildIdDistinctFromTargetBuildId: "measurementBuildId identifies the Great Scale measurement build; targetBuildId identifies the Control Plane acceptance build. These are independent identities and must not be assumed equal.",
      targetBuildIdToResidualBuildId: "targetBuildId must equal final G0-G6 attestation.buildId and becomes residual.buildId.",
      targetSourceRevisionToAttestationSource: "target.repository/commitSha must equal final G0-G6 attestation.source.repository/commitSha.",
      targetArtifactDigestToAcceptanceArtifact: "targetArtifact.digest must equal final G0-G6 attestation.artifact.digest.",
      sourceCommitEqualsWorkflowHead: "source.commitSha must equal execution.headSha",
      measurementArtifactBinding: "artifact.digest identifies the Great Scale model/measurement artifact and model.inputDigest binds its inputs; verify independently and never substitute it for targetArtifact.digest.",
      trustBoundary: "verify Ed25519 against an independently configured public key; receipt cannot choose its trust anchor",
    },
  });

  const rawSchema = readFileSync(new URL("./contracts/g6-residual-measurement/v1.schema.json", import.meta.url), "utf8");
  const gitBlobHeader = Buffer.from(`blob ${Buffer.byteLength(rawSchema, "utf8")}\0`, "utf8");
  const actualBlobSha = createHash("sha1").update(gitBlobHeader).update(rawSchema, "utf8").digest("hex");
  assert.equal(actualBlobSha, contract.schemaBlobSha, "registry pins the exact schema blob, not just a path");

  const schema = JSON.parse(rawSchema);
  assert.equal(schema.properties.measurement.properties.STopological.minimum, 0);
  assert.equal(schema.properties.measurement.properties.STopological.maximum, 0.25);
  assert.equal(schema.properties.measuredAt.format, "date-time");
  assert.equal(schema.properties.signatureAlgorithm.const, "Ed25519");
  assert.equal(schema.properties.numericalCertification.additionalProperties, false);
  assert.equal(schema.properties.numericalCertification.properties.verified.const, true);
  assert.equal(schema.properties.numericalCertification.properties.proofDigest.pattern, "^[a-f0-9]{64}$");
  assert.ok(schema.required.includes("measurementBuildId"));
  assert.ok(schema.required.includes("targetBuildId"));
  assert.ok(!schema.required.includes("buildId"));
  assert.equal(schema.properties.target.properties.repository.const, "doitupsolutions810-crow/living-intermediate-control-plane");
  assert.equal(schema.properties.targetArtifact.properties.digest.pattern, "^sha256:[a-f0-9]{64}$");
  assert.match(schema.properties.measurementBuildId.description, /must not be assumed equal/i);
  assert.match(schema.properties.targetBuildId.description, /must equal the final G0-G6 production acceptance attestation buildId/i);
  assert.match(schema.properties.artifact.properties.digest.description, /distinct from targetArtifact.digest/i);
});

test("G6 measurement schema contract cannot silently change or claim to be a producer", () => {
  const changedSha = structuredClone(baseline);
  changedSha.g6ResidualMeasurementContract.schemaBlobSha = "f".repeat(40);
  assert.ok(validateRepositoryMap(changedSha).some(message => message.includes("g6ResidualMeasurementContract")));

  const forgedProducer = structuredClone(baseline);
  forgedProducer.g6ResidualMeasurementContract.status = "verified";
  assert.ok(validateRepositoryMap(forgedProducer).some(message => message.includes("g6ResidualMeasurementContract")));

  const changedMapping = structuredClone(baseline);
  changedMapping.g6ResidualMeasurementContract.mapping.measurementSTopologicalToResidualS = "measurement.raw -> residual.S";
  assert.ok(validateRepositoryMap(changedMapping).some(message => message.includes("g6ResidualMeasurementContract")));

  const ambiguousBuildId = structuredClone(baseline);
  ambiguousBuildId.g6ResidualMeasurementContract.mapping.targetBuildIdToResidualBuildId = "targetBuildId -> residual.buildId without target artifact binding";
  assert.ok(validateRepositoryMap(ambiguousBuildId).some(message => message.includes("g6ResidualMeasurementContract")));
});
