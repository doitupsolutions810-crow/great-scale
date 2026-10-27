import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { qiWuZhangGlobalGeometry } = require("./research/topological-qgt.cjs");
const { CONE } = require("./public/scale.cjs");
const schema = JSON.parse(readFileSync(new URL("./contracts/g6-residual-measurement/v1.schema.json", import.meta.url), "utf8"));

const measurementFields = [
  "chernNumber", "rawChernNumber", "chernIntegerResidual", "integratedCurvature",
  "absoluteCurvatureBudget", "positiveCurvatureBudget", "negativeCurvatureBudget",
  "curvatureCancellationBudget", "metricAreaBudget", "topologicalFloor", "metricAreaExcess",
  "topologicalSaturationRaw", "topologicalSaturation", "signedTopologicalPolarization",
  "STopological", "psiTopological", "acceptedPsiTopological",
  "curvatureOrientationEntropyResidual", "curvatureChernResidual",
  "curvatureCancellationIdentityResidual", "curvatureOrientationVarianceResidual",
  "rigorousCurvatureErrorBound", "rigorousMetricAreaErrorBound", "rigorousBoundFinite",
  "gridAlignmentCurvatureDiscrepancy", "gridAlignmentAreaDiscrepancy",
  "quadratureTolerance", "quadratureConverged", "topologicalMappingValid",
  "refinementCount", "refinedGridSize"
];

test("G6 schema requires source/build/run/artifact/model/digest/signature bindings", () => {
  assert.equal(schema.$schema, "https://json-schema.org/draft/2020-12/schema");
  assert.equal(schema.properties.schema.const, "great-scale.g6-residual-measurement/v1");
  assert.equal(schema.properties.issuer.const, "great-scale-g6-residual-measurer");
  assert.equal(schema.properties.environment.const, "production");
  assert.equal(schema.additionalProperties, false);
  for (const key of [
    "source", "execution", "artifact", "model", "measurement",
    "measurementBuildId", "targetBuildId", "target", "targetArtifact",
    "measuredAt", "generatedAt", "expiresAt", "canonicalization",
    "signatureAlgorithm", "keyId", "digest", "signature"
  ]) assert.ok(schema.required.includes(key), "missing top-level requirement: " + key);
  assert.ok(!schema.required.includes("buildId"),
    "ambiguous buildId must not collapse measurement and target build identities");
  assert.match(schema.properties.measurementBuildId.description,
    /must not be assumed equal to the target Control Plane acceptance build ID/i);
  assert.match(schema.properties.targetBuildId.description,
    /must equal the final G0-G6 production acceptance attestation buildId/i);
  assert.equal(schema.properties.target.properties.repository.const,
    "doitupsolutions810-crow/living-intermediate-control-plane");
  assert.equal(schema.properties.targetArtifact.properties.digest.pattern, "^sha256:[a-f0-9]{64}$");
  assert.equal(schema.properties.source.properties.repository.const,
    "doitupsolutions810-crow/great-scale");
  assert.equal(schema.properties.execution.properties.conclusion.const, "success");
  assert.equal(schema.properties.model.properties.id.const, "qi-wu-zhang-two-band");
  assert.equal(schema.properties.measurement.additionalProperties, false);
});

test("G6 schema preserves all numerical diagnostics emitted by the topological QGT model", () => {
  const required = schema.properties.measurement.required;
  assert.deepEqual(required, measurementFields);
  const result = qiWuZhangGlobalGeometry(-1, 40);
  for (const key of measurementFields) {
    assert.ok(Object.hasOwn(result, key), "model result is missing G6 field: " + key);
    if (key === "rigorousBoundFinite" || key === "quadratureConverged" || key === "topologicalMappingValid") {
      assert.equal(typeof result[key], "boolean", key + " must be boolean");
    } else {
      assert.equal(typeof result[key], "number", key + " must be numeric");
      assert.ok(Number.isFinite(result[key]), key + " must be finite");
    }
  }
  assert.equal(result.topologicalMappingValid, true);
  assert.equal(result.quadratureConverged, true);
  assert.equal(result.rigorousBoundFinite, true);
});

test("accepted G6 scalar is algebraically bound to signed topological polarization", () => {
  const result = qiWuZhangGlobalGeometry(-1, 40);
  assert.equal(result.topologicalMappingValid, true);
  assert.ok(Math.abs(result.topologicalFloor - Math.abs(result.chernNumber)) <= result.quadratureTolerance);
  assert.ok(Math.abs(result.metricAreaExcess -
    (result.metricAreaBudget - result.topologicalFloor)) <= result.quadratureTolerance);
  assert.ok(Math.abs(result.signedTopologicalPolarization -
    Math.sign(result.chernNumber) * result.topologicalSaturation) <= 1e-12);
  assert.ok(Math.abs(result.STopological -
    (1 - result.topologicalSaturation ** 2) / 4) <= 1e-12);
  assert.ok(Math.abs(result.psiTopological - (CONE + result.STopological)) <= 1e-12);
  assert.ok(Math.abs(result.acceptedPsiTopological - result.psiTopological) <= 1e-12);
  assert.ok(result.curvatureChernResidual <= result.quadratureTolerance);
  assert.ok(result.rigorousCurvatureErrorBound <= result.quadratureTolerance);
  assert.ok(result.rigorousMetricAreaErrorBound <= result.quadratureTolerance);
});

test("under-resolved model output cannot be promoted as a G6 measurement", () => {
  const result = qiWuZhangGlobalGeometry(-1.99, 40);
  assert.equal(result.topologicalMappingValid, false);
  assert.equal(result.acceptedPsiTopological, null);
  assert.ok(result.rigorousBoundFinite === false ||
    result.rigorousCurvatureErrorBound > result.quadratureTolerance ||
    result.rigorousMetricAreaErrorBound > result.quadratureTolerance ||
    result.curvatureChernResidual > result.quadratureTolerance);
});

test("contract makes the full signed/absolute curvature and convergence data mandatory", () => {
  for (const key of [
    "chernNumber", "integratedCurvature", "absoluteCurvatureBudget",
    "positiveCurvatureBudget", "negativeCurvatureBudget", "metricAreaBudget",
    "metricAreaExcess", "signedTopologicalPolarization", "STopological",
    "rigorousCurvatureErrorBound", "rigorousMetricAreaErrorBound",
    "gridAlignmentCurvatureDiscrepancy", "gridAlignmentAreaDiscrepancy",
    "quadratureTolerance", "quadratureConverged", "topologicalMappingValid"
  ]) assert.ok(schema.properties.measurement.required.includes(key), key + " must not be dropped");
  assert.ok(schema.properties.model.properties.inputDigest.pattern.includes("a-f"));
  assert.ok(schema.properties.digest.pattern.includes("a-f"));
  assert.ok(schema.properties.signature.pattern.includes("A-Za-z0-9"));
});
