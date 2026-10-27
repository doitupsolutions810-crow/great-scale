import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const schema = JSON.parse(readFileSync(
  new URL("./contracts/g6-residual-measurement/v1.schema.json", import.meta.url),
  "utf8",
));

test("G6 measurement schema is versioned, closed, and explicitly non-authorizing by itself", () => {
  assert.equal(schema.$schema, "https://json-schema.org/draft/2020-12/schema");
  assert.equal(schema.title, "Great Scale G6 Residual Measurement v1");
  assert.equal(schema.properties.schema.const, "great-scale.g6-residual-measurement/v1");
  assert.equal(schema.properties.issuer.const, "great-scale-g6-residual-measurer");
  assert.equal(schema.properties.environment.const, "production");
  assert.equal(schema.additionalProperties, false);
  assert.match(schema.description, /does not prove signature authenticity/i);
  assert.match(schema.description, /production authorization/i);
  assert.deepEqual([...schema.required].sort(), Object.keys(schema.properties).sort());
});

test("source revision and workflow evidence have strict identities and formats", () => {
  const source = schema.properties.source;
  assert.equal(source.additionalProperties, false);
  assert.deepEqual([...source.required].sort(), ["commitSha", "repository"]);
  assert.equal(source.properties.repository.const, "doitupsolutions810-crow/great-scale");
  assert.equal(source.properties.commitSha.pattern, "^[a-f0-9]{40}$");

  const execution = schema.properties.execution;
  assert.equal(execution.additionalProperties, false);
  assert.deepEqual([...execution.required].sort(), [
    "runId", "runAttempt", "runUrl", "headSha", "conclusion", "startedAt", "completedAt"
  ].sort());
  assert.equal(execution.properties.runId.minimum, 1);
  assert.equal(execution.properties.runAttempt.minimum, 1);
  assert.equal(execution.properties.conclusion.const, "success");
  assert.equal(execution.properties.headSha.pattern, "^[a-f0-9]{40}$");
  assert.match(execution.properties.runUrl.pattern, /actions\/runs/);
  assert.equal(execution.properties.startedAt.format, "date-time");
  assert.equal(execution.properties.completedAt.format, "date-time");
});

test("artifact and model provenance are versioned and bounded", () => {
  const artifact = schema.properties.artifact;
  assert.equal(artifact.additionalProperties, false);
  assert.deepEqual([...artifact.required].sort(), ["name", "digest"]);
  assert.equal(artifact.properties.digest.pattern, "^sha256:[a-f0-9]{64}$");

  const model = schema.properties.model;
  assert.equal(model.additionalProperties, false);
  assert.equal(model.properties.id.const, "qi-wu-zhang-two-band");
  assert.equal(model.properties.inputDigest.pattern, "^[a-f0-9]{64}$");
  const parameters = model.properties.parameters;
  assert.equal(parameters.additionalProperties, false);
  assert.deepEqual([...parameters.required].sort(), ["m", "gridSize", "maxRefinements"].sort());
  assert.equal(parameters.properties.gridSize.minimum, 4);
  assert.equal(parameters.properties.gridSize.maximum, 4096);
  assert.equal(parameters.properties.maxRefinements.minimum, 1);
  assert.equal(parameters.properties.maxRefinements.maximum, 5);
});

test("measurement build identity is distinct from target build and release artifact identities", () => {
  assert.ok(schema.required.includes("measurementBuildId"));
  assert.ok(schema.required.includes("targetBuildId"));
  assert.ok(!schema.required.includes("buildId"), "a single ambiguous buildId must not serve both services");
  assert.match(schema.properties.measurementBuildId.description,
    /must not be assumed equal to the target Control Plane acceptance build ID/i);
  assert.match(schema.properties.targetBuildId.description,
    /must equal the final G0-G6 production acceptance attestation buildId/i);
  assert.equal(schema.properties.target.properties.repository.const,
    "doitupsolutions810-crow/living-intermediate-control-plane");
  assert.equal(schema.properties.target.properties.commitSha.pattern, "^[a-f0-9]{40}$");
  assert.equal(schema.properties.targetArtifact.properties.digest.pattern, "^sha256:[a-f0-9]{64}$");
  assert.match(schema.properties.targetArtifact.properties.digest.description,
    /must match the final G0-G6 attestation artifact.digest/i);
  assert.match(schema.properties.artifact.description, /Great Scale model\/measurement artifact/i);
  assert.match(schema.properties.artifact.properties.digest.description, /distinct from targetArtifact.digest/i);
});

test("measurement contains explicit QGT, convergence, topology, and error-bound diagnostics", () => {
  const measurement = schema.properties.measurement;
  assert.equal(measurement.additionalProperties, false);
  assert.deepEqual([...measurement.required].sort(), Object.keys(measurement.properties).sort());

  const properties = measurement.properties;
  assert.equal(properties.STopological.minimum, 0);
  assert.equal(properties.STopological.maximum, 0.25);
  assert.equal(properties.topologicalSaturation.minimum, 0);
  assert.equal(properties.topologicalSaturation.maximum, 1);
  assert.equal(properties.signedTopologicalPolarization.minimum, -1);
  assert.equal(properties.signedTopologicalPolarization.maximum, 1);
  assert.equal(properties.quadratureConverged.const, true);
  assert.equal(properties.topologicalMappingValid.const, true);
  assert.equal(properties.errorEstimatesFinite.const, true);
  assert.equal(properties.errorBoundMethod.const, "richardson-asymptotic-estimate-only");
  assert.ok(properties.curvatureErrorEstimateWithSafetyFactor.minimum >= 0);
  assert.ok(properties.metricAreaErrorEstimateWithSafetyFactor.minimum >= 0);
  assert.match(measurement.description, /do not establish a rigorous quadrature bound/i);
  assert.ok(properties.gridAlignmentCurvatureDiscrepancy.minimum >= 0);
  assert.ok(properties.gridAlignmentAreaDiscrepancy.minimum >= 0);
  assert.equal(properties.quadratureTolerance.exclusiveMinimum, 0, 'exclusiveMinimum 0 means tolerance must be strictly positive');
  assert.match(measurement.description, /STopological/);
  assert.match(measurement.description, /residual\.S/);
});

test("G6 requires a separate independent numerical certificate; Richardson estimates cannot certify themselves", () => {
  const certification = schema.properties.numericalCertification;
  assert.ok(schema.required.includes("numericalCertification"));
  assert.equal(certification.additionalProperties, false);
  assert.deepEqual([...certification.required].sort(), [
    "method", "verifierId", "sourceCommitSha", "modelInputDigest",
    "curvatureErrorUpperBound", "metricAreaErrorUpperBound",
    "evidenceUrl", "proofDigest", "verified",
    "certificateKeyId", "certificateSignature", "generatedAt", "expiresAt", "measurementDigest"
  ].sort());
  assert.deepEqual(certification.properties.method.enum,
    ["interval-enclosure-v1", "analytic-derivative-bound-v1"]);
  assert.equal(certification.properties.verified.const, true);
  assert.equal(certification.properties.certificateKeyId.pattern, "^[A-Za-z0-9._:-]+$");
  assert.equal(certification.properties.certificateSignature.pattern, "^[A-Za-z0-9+/]{86}==$");
  assert.equal(certification.properties.generatedAt.format, "date-time");
  assert.equal(certification.properties.expiresAt.format, "date-time");
  assert.equal(certification.properties.measurementDigest.pattern, "^[a-f0-9]{64}$");
  assert.match(certification.properties.measurementDigest.description, /exact QGT output/i);
  assert.match(certification.properties.certificateSignature.description,
    /independently pinned certificate public key/i);
  assert.match(certification.description, /schema shape alone are not proof/i);
  assert.equal(schema.properties.measurement.properties.errorBoundMethod.const,
    "richardson-asymptotic-estimate-only");
  assert.match(schema.description, /numerical-certificate-validity/i);
});

test("measurement timestamp, canonicalization, digest, and Ed25519 signature are explicit", () => {
  assert.ok(schema.required.includes("measuredAt"));
  assert.equal(schema.properties.measuredAt.format, "date-time");
  assert.match(schema.properties.measuredAt.description, /residual\.measuredAt/);
  assert.equal(schema.properties.canonicalization.const, "great-scale.canonical-json/v1");
  assert.match(schema.properties.canonicalization.description, /sorted object keys/i);
  assert.equal(schema.properties.signatureAlgorithm.const, "Ed25519");
  assert.match(schema.properties.signatureAlgorithm.description, /deployment-pinned public key/i);
  assert.equal(schema.properties.digest.pattern, "^[a-f0-9]{64}$");
  assert.match(schema.properties.digest.description, /SHA-256/);
  assert.equal(schema.properties.signature.pattern, "^[A-Za-z0-9+/]{86}==$");
  assert.match(schema.properties.signature.description, /Ed25519 signature/i);
});

test("the schema declares the downstream mapping but does not pretend to verify cross-field truth", () => {
  assert.match(schema.properties.measurement.description, /must be mapped to residual\.S/);
  assert.match(schema.description, /cross-field binding/i);
  assert.match(schema.description, /live observation/i);
});

test("target commit and target artifact are required independently of Great Scale measurement provenance", () => {
  assert.ok(schema.required.includes("target"));
  assert.ok(schema.required.includes("targetArtifact"));
  assert.equal(schema.properties.target.additionalProperties, false);
  assert.equal(schema.properties.targetArtifact.additionalProperties, false);
  assert.deepEqual([...schema.properties.target.required].sort(), ["commitSha", "repository"]);
  assert.deepEqual([...schema.properties.targetArtifact.required].sort(), ["digest", "name"]);
  assert.match(schema.properties.target.description, /must match the source identity in the final G0-G6 acceptance attestation/i);
  assert.match(schema.description, /must not be conflated/i);
});
