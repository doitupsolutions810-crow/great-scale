import test from "node:test";
import assert from "node:assert/strict";
import { createHash, generateKeyPairSync, sign } from "node:crypto";
import {
  canonicalG6CertificateJson,
  G6_NUMERICAL_CERTIFICATE_SCHEMA,
  fetchAndVerifyG6NumericalCertification,
  fetchG6NumericalProofBytes,
  verifyG6NumericalCertification
} from "./lib/g6-numerical-certificate.mjs";

const { privateKey, publicKey } = generateKeyPairSync("ed25519");
const publicKeyPem = publicKey.export({ type: "spki", format: "pem" });
const keyId = "qgt-independent-certifier-key-v1";
const verifierId = "great-scale-certified-numerics-v1";
const sourceCommitSha = "a".repeat(40);
const modelInputDigest = "b".repeat(64);
const allowedEvidenceOrigins = ["https://evidence.example.invalid"];
const evidenceUrl = "https://evidence.example.invalid/certificates/qgt-proof.json";
const now = Date.now();
const measurement = {
  quadratureTolerance: 1e-3,
  STopological: 0.125,
  topologicalMappingValid: true,
  quadratureConverged: true,
  errorEstimatesFinite: true,
  errorBoundMethod: "richardson-asymptotic-estimate-only"
};

function sha256(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
}

function fixture({ certificationOverrides = {}, proofOverrides = {}, measured = measurement } = {}) {
  const measurementDigest = sha256(Buffer.from(canonicalG6CertificateJson(measured), "utf8"));
  const certification = {
    method: "interval-enclosure-v1",
    verifierId,
    sourceCommitSha,
    modelInputDigest,
    measurementDigest,
    curvatureErrorUpperBound: 1e-4,
    metricAreaErrorUpperBound: 2e-4,
    evidenceUrl,
    proofDigest: "",
    verified: true,
    certificateKeyId: keyId,
    certificateSignature: "",
    generatedAt: new Date(now - 1000).toISOString(),
    expiresAt: new Date(now + 60_000).toISOString(),
    ...certificationOverrides
  };
  const proof = {
    schema: G6_NUMERICAL_CERTIFICATE_SCHEMA,
    method: certification.method,
    verifierId: certification.verifierId,
    sourceCommitSha: certification.sourceCommitSha,
    modelInputDigest: certification.modelInputDigest,
    measurementDigest: certification.measurementDigest,
    curvatureErrorUpperBound: certification.curvatureErrorUpperBound,
    metricAreaErrorUpperBound: certification.metricAreaErrorUpperBound,
    generatedAt: certification.generatedAt,
    expiresAt: certification.expiresAt,
    witness: { enclosureCellCount: 128, checkedFiniteDenominators: true },
    ...proofOverrides
  };
  const proofBytes = Buffer.from(JSON.stringify(proof), "utf8");
  if (!Object.hasOwn(certificationOverrides, "proofDigest")) {
    certification.proofDigest = sha256(proofBytes);
  }
  const { certificateSignature, ...unsigned } = certification;
  certification.certificateSignature = sign(
    null, Buffer.from(canonicalG6CertificateJson(unsigned), "utf8"), privateKey
  ).toString("base64");
  return { certification, proofBytes, measurement: measured };
}

function options(candidate, overrides = {}) {
  return {
    certification: candidate.certification,
    proofBytes: candidate.proofBytes,
    publicKeyPem,
    trustedCertificateKeyId: keyId,
    trustedVerifierId: verifierId,
    sourceCommitSha,
    modelInputDigest,
    measurement: candidate.measurement,
    allowedEvidenceOrigins,
    now,
    ...overrides
  };
}

function responseAt(url, body, init = {}) {
  const response = new Response(body, {
    ...init,
    headers: { "content-type": "application/json", ...(init.headers || {}) }
  });
  Object.defineProperty(response, "url", { value: url, configurable: true });
  return response;
}

test("independent signed numerical certificate verifies and binds the exact measurement and proof bytes", async () => {
  const candidate = fixture();
  const result = verifyG6NumericalCertification(options(candidate));
  assert.equal(result.valid, true, result.failures.join(","));
  assert.deepEqual(result.failures, []);
  assert.equal(result.certificate.method, "interval-enclosure-v1");
  assert.equal(result.certificate.measurementDigest, candidate.certification.measurementDigest);

  const fetched = await fetchAndVerifyG6NumericalCertification({
    ...options(candidate),
    fetchImpl: async (url, init) => {
      assert.equal(String(url), evidenceUrl);
      assert.equal(init.redirect, "error");
      assert.equal(init.cache, "no-store");
      assert.equal(init.headers["cache-control"], "no-cache");
      return responseAt(evidenceUrl, candidate.proofBytes);
    }
  });
  assert.equal(fetched.valid, true, fetched.failures.join(","));
});

test("missing trust pins and an untrusted certificate key ID fail closed", () => {
  const candidate = fixture();
  assert.equal(verifyG6NumericalCertification(options(candidate, {
    publicKeyPem: "",
    trustedCertificateKeyId: "",
    trustedVerifierId: ""
  })).valid, false);
  assert.ok(verifyG6NumericalCertification(options(candidate, {
    trustedCertificateKeyId: "other-key"
  })).failures.includes("numerical_certificate_key_id_mismatch"));
});

test("wrong source commit, model input, and measurement digest are independently rejected", () => {
  const candidate = fixture();
  assert.ok(verifyG6NumericalCertification(options(candidate, {
    sourceCommitSha: "c".repeat(40)
  })).failures.includes("numerical_certification_source_commit_mismatch"));
  assert.ok(verifyG6NumericalCertification(options(candidate, {
    modelInputDigest: "d".repeat(64)
  })).failures.includes("numerical_certification_model_input_digest_mismatch"));
  const changedMeasurement = { ...candidate.measurement, STopological: 0.2 };
  assert.ok(verifyG6NumericalCertification(options(candidate, {
    measurement: changedMeasurement
  })).failures.includes("numerical_certification_measurement_digest_mismatch"));
});

test("certified upper bounds above the measured quadrature tolerance cannot authorize G6", () => {
  const candidate = fixture({
    certificationOverrides: {
      curvatureErrorUpperBound: 0.002,
      metricAreaErrorUpperBound: 0.003
    }
  });
  const result = verifyG6NumericalCertification(options(candidate));
  assert.equal(result.valid, false);
  assert.ok(result.failures.includes("certified_curvature_error_exceeds_tolerance_or_invalid"));
  assert.ok(result.failures.includes("certified_metric_area_error_exceeds_tolerance_or_invalid"));
});

test("an authentic certificate cannot promote an out-of-domain or failed QGT measurement", () => {
  const invalidCases = [
    [{ ...measurement, STopological: -0.001 }, "measurement_topological_residual_out_of_domain"],
    [{ ...measurement, STopological: 0.250001 }, "measurement_topological_residual_out_of_domain"],
    [{ ...measurement, topologicalMappingValid: false }, "measurement_topological_mapping_invalid"],
    [{ ...measurement, quadratureConverged: false }, "measurement_quadrature_not_converged"],
    [{ ...measurement, errorEstimatesFinite: false }, "measurement_empirical_estimates_not_finite"],
    [{ ...measurement, errorBoundMethod: "heuristic-bound" }, "measurement_empirical_error_method_mismatch"],
  ];
  for (const [measured, expectedFailure] of invalidCases) {
    const candidate = fixture({ measured });
    const result = verifyG6NumericalCertification(options(candidate));
    assert.equal(result.valid, false, `rejects ineligible measurement: ${expectedFailure}`);
    assert.ok(result.failures.includes(expectedFailure), result.failures.join(","));
  }
});

test("expired, malformed, or future numerical certificates are rejected", () => {
  const expired = fixture({
    certificationOverrides: {
      generatedAt: new Date(now - 10 * 60_000).toISOString(),
      expiresAt: new Date(now - 1000).toISOString()
    }
  });
  const expiredResult = verifyG6NumericalCertification(options(expired));
  assert.ok(expiredResult.failures.includes("numerical_certificate_stale"));
  assert.ok(expiredResult.failures.includes("numerical_certificate_expired"));

  const malformed = fixture({
    certificationOverrides: { generatedAt: "October 27, 2026 00:00:00 GMT" }
  });
  assert.ok(verifyG6NumericalCertification(options(malformed)).failures
    .includes("numerical_certificate_timestamps_invalid"));

  const future = fixture({
    certificationOverrides: {
      generatedAt: new Date(now + 60_000).toISOString(),
      expiresAt: new Date(now + 120_000).toISOString()
    }
  });
  assert.ok(verifyG6NumericalCertification(options(future)).failures
    .includes("numerical_certificate_generated_in_future"));
});

test("changed proof bytes, mismatched proof fields, and certificate signature tampering fail", () => {
  const candidate = fixture();
  const tamperedBytes = Buffer.from(candidate.proofBytes.toString("utf8") + " ");
  assert.ok(verifyG6NumericalCertification(options(candidate, {
    proofBytes: tamperedBytes
  })).failures.includes("numerical_proof_digest_mismatch"));

  const mismatched = fixture({ proofOverrides: { sourceCommitSha: "f".repeat(40) } });
  assert.ok(verifyG6NumericalCertification(options(mismatched)).failures
    .includes("numerical_proof_sourceCommitSha_mismatch"));

  const badSignature = {
    ...candidate.certification,
    certificateSignature: "A".repeat(86) + "=="
  };
  assert.ok(verifyG6NumericalCertification(options({
    ...candidate, certification: badSignature
  })).failures.includes("numerical_certificate_signature_invalid"));
});

test("invalid freshness policy values fail closed instead of disabling timestamp checks", () => {
  const candidate = fixture();
  assert.ok(verifyG6NumericalCertification(options(candidate, { now: NaN }))
    .failures.includes("verification_clock_invalid"));
  assert.ok(verifyG6NumericalCertification(options(candidate, { maxAgeMs: Infinity }))
    .failures.includes("numerical_certificate_max_age_policy_invalid"));
  assert.ok(verifyG6NumericalCertification(options(candidate, { maxClockSkewMs: NaN }))
    .failures.includes("numerical_certificate_clock_skew_policy_invalid"));
});

test("non-canonicalizable measurements cannot be certified", () => {
  const candidate = fixture();
  const malformedMeasurement = { quadratureTolerance: 1e-3, impossible: 1n };
  const result = verifyG6NumericalCertification(options(candidate, {
    measurement: malformedMeasurement
  }));
  assert.equal(result.valid, false);
  assert.ok(result.failures.includes("measurement_not_canonicalizable"));
  assert.ok(result.failures.includes("numerical_certification_measurement_digest_mismatch"));
});

test("the proof URL is HTTPS and pinned to an explicitly allowed origin", async () => {
  let calls = 0;
  const candidate = fixture({
    certificationOverrides: { evidenceUrl: "https://attacker.example.invalid/proof.json" }
  });
  const fetched = await fetchG6NumericalProofBytes({
    url: candidate.certification.evidenceUrl,
    allowedEvidenceOrigins,
    fetchImpl: async () => { calls++; throw new Error("must not fetch a disallowed origin"); }
  });
  assert.equal(fetched.valid, false);
  assert.equal(fetched.failures[0], "numerical_proof_url_not_pinned_https");
  assert.equal(calls, 0);

  const insecure = await fetchG6NumericalProofBytes({
    url: "http://evidence.example.invalid/certificates/qgt-proof.json",
    allowedEvidenceOrigins,
    fetchImpl: async () => { calls++; throw new Error("must not fetch HTTP"); }
  });
  assert.equal(insecure.valid, false);
  assert.equal(calls, 0);
});

test("proof fetch rejects redirects, wrong final URLs, and oversized bodies", async () => {
  const redirect = await fetchG6NumericalProofBytes({
    url: evidenceUrl,
    allowedEvidenceOrigins,
    fetchImpl: async url => responseAt(String(url), "", {
      status: 302, headers: { location: "https://evidence.example.invalid/elsewhere" }
    })
  });
  assert.equal(redirect.valid, false);
  assert.equal(redirect.failures[0], "numerical_proof_response_identity_invalid");

  const wrongFinal = await fetchG6NumericalProofBytes({
    url: evidenceUrl,
    allowedEvidenceOrigins,
    fetchImpl: async () => responseAt("https://evidence.example.invalid/other.json", "{}")
  });
  assert.equal(wrongFinal.valid, false);

  const oversized = await fetchG6NumericalProofBytes({
    url: evidenceUrl,
    allowedEvidenceOrigins,
    maxBytes: 8,
    fetchImpl: async url => responseAt(String(url), JSON.stringify({ witness: "much larger than 8 bytes" }))
  });
  assert.equal(oversized.valid, false);
  assert.ok(oversized.failures.includes("numerical_proof_content_length_invalid") ||
    oversized.failures.includes("numerical_proof_body_too_large"));
});
