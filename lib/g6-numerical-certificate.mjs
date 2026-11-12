import { createHash, createPublicKey, verify as verifySignature } from "node:crypto";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { CONE } = require("../public/scale.cjs");

export const G6_NUMERICAL_CERTIFICATE_SCHEMA = "great-scale.qgt-numerical-proof/v1";
export const G6_NUMERICAL_CERTIFICATE_METHODS = Object.freeze([
  "interval-enclosure-v1",
  "analytic-derivative-bound-v1"
]);

const SHA256_HEX = /^[a-f0-9]{64}$/;
const FULL_SHA = /^[a-f0-9]{40}$/;
const ED25519_SIGNATURE = /^[A-Za-z0-9+/]{86}==$/;
const RFC3339 = /^[0-9]{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12][0-9]|3[01])T(?:[01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](?:\.[0-9]+)?(?:Z|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])$/;
const DEFAULT_TIMEOUT_MS = 3000;
const DEFAULT_MAX_BYTES = 1024 * 1024;
const HARD_MAX_BYTES = 4 * 1024 * 1024;

export const G6_NUMERICAL_CERTIFICATION_FIELDS = Object.freeze([
  "method", "verifierId", "sourceCommitSha", "modelInputDigest", "measurementDigest",
  "curvatureErrorUpperBound", "metricAreaErrorUpperBound", "evidenceUrl", "proofDigest",
  "verified", "certificateKeyId", "certificateSignature", "generatedAt", "expiresAt"
]);
export const G6_MEASUREMENT_FIELDS = Object.freeze([
  "chernNumber", "rawChernNumber", "chernIntegerResidual", "integratedCurvature",
  "absoluteCurvatureBudget", "positiveCurvatureBudget", "negativeCurvatureBudget",
  "curvatureCancellationBudget", "metricAreaBudget", "topologicalFloor", "metricAreaExcess",
  "topologicalSaturationRaw", "topologicalSaturation", "signedTopologicalPolarization",
  "STopological", "psiTopological", "acceptedPsiTopological",
  "curvatureOrientationEntropyResidual", "curvatureChernResidual",
  "curvatureCancellationIdentityResidual", "curvatureOrientationVarianceResidual",
  "gridAlignmentCurvatureDiscrepancy", "gridAlignmentAreaDiscrepancy",
  "quadratureTolerance", "quadratureConverged", "topologicalMappingValid",
  "refinementCount", "refinedGridSize", "curvatureErrorEstimateWithSafetyFactor",
  "metricAreaErrorEstimateWithSafetyFactor", "errorEstimatesFinite", "errorBoundMethod"
]);
const NUMERIC_MEASUREMENT_FIELDS = Object.freeze(G6_MEASUREMENT_FIELDS.filter(
  field => !["quadratureConverged", "topologicalMappingValid", "errorEstimatesFinite", "errorBoundMethod"].includes(field)
));
const PROOF_FIELDS = Object.freeze([
  "schema", "method", "verifierId", "sourceCommitSha", "modelInputDigest", "measurementDigest",
  "curvatureErrorUpperBound", "metricAreaErrorUpperBound", "generatedAt", "expiresAt", "witness"
]);

export function canonicalG6CertificateJson(value) {
  if (Array.isArray(value)) {
    return "[" + value.map(item => canonicalG6CertificateJson(item)).join(",") + "]";
  }
  if (value && typeof value === "object") {
    return "{" + Object.keys(value).sort().map(key =>
      JSON.stringify(key) + ":" + canonicalG6CertificateJson(value[key])).join(",") + "}";
  }
  const encoded = JSON.stringify(value);
  if (encoded === undefined) throw new TypeError("value is not JSON-canonicalizable");
  return encoded;
}

function sha256Hex(value) {
  return createHash("sha256").update(value).digest("hex");
}

function exactKeys(value, expected) {
  return value !== null &&
    typeof value === "object" &&
    !Array.isArray(value) &&
    JSON.stringify(Object.keys(value).sort()) === JSON.stringify([...expected].sort());
}

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function validTimestamp(value) {
  if (typeof value !== "string" || !RFC3339.test(value)) return false;
  const parsed = Date.parse(value);
  if (!Number.isFinite(parsed)) return false;
  const date = value.slice(0, 10);
  const dayStart = Date.parse(date + "T00:00:00.000Z");
  return Number.isFinite(dayStart) && new Date(dayStart).toISOString().slice(0, 10) === date;
}

function binaryEntropyNats(probability) {
  if (!Number.isFinite(probability) || probability < 0 || probability > 1) return NaN;
  const p = Math.max(0, Math.min(1, probability));
  const left = p > 0 ? -p * Math.log(p) : 0;
  const right = p < 1 ? -(1 - p) * Math.log1p(-p) : 0;
  return left + right;
}

function closeEnough(actual, expected, tolerance) {
  return typeof actual === "number" && Number.isFinite(actual) &&
    Number.isFinite(expected) && Math.abs(actual - expected) <= tolerance;
}

function validateG6Measurement(measurement, maxQuadratureTolerance) {
  const failures = [];
  const add = code => failures.push(code);
  if (!isObject(measurement) || !exactKeys(measurement, G6_MEASUREMENT_FIELDS)) {
    return ["g6_measurement_fields_not_exact"];
  }
  for (const key of NUMERIC_MEASUREMENT_FIELDS) {
    if (typeof measurement[key] !== "number" || !Number.isFinite(measurement[key])) {
      add("g6_measurement_numeric_field_invalid:" + key);
    }
  }
  if (failures.length) return failures;

  const tolerance = measurement.quadratureTolerance;
  if (!Number.isFinite(maxQuadratureTolerance) || maxQuadratureTolerance <= 0) {
    add("g6_max_quadrature_tolerance_pin_missing_or_invalid");
  } else if (tolerance <= 0 || tolerance > maxQuadratureTolerance) {
    add("g6_quadrature_tolerance_outside_deployment_policy");
  }
  if (!Number.isInteger(measurement.chernNumber)) add("g6_chern_number_not_integer");
  if (measurement.chernIntegerResidual < 0 || measurement.chernIntegerResidual > 1e-6) add("g6_chern_integer_residual_invalid");
  if (measurement.quadratureConverged !== true) add("measurement_quadrature_not_converged");
  if (measurement.topologicalMappingValid !== true) add("measurement_topological_mapping_invalid");
  if (measurement.errorEstimatesFinite !== true) add("measurement_empirical_estimates_not_finite");
  if (measurement.errorBoundMethod !== "richardson-asymptotic-estimate-only") add("measurement_empirical_error_method_mismatch");
  if (!(measurement.metricAreaBudget > 1e-12)) add("g6_metric_area_budget_invalid");
  if (measurement.positiveCurvatureBudget < 0 || measurement.negativeCurvatureBudget < 0 ||
      measurement.absoluteCurvatureBudget < 0 || measurement.curvatureCancellationBudget < 0) {
    add("g6_curvature_budget_invalid");
  }
  if (measurement.topologicalSaturation < 0 || measurement.topologicalSaturation > 1) add("g6_topological_saturation_out_of_range");
  if (measurement.STopological < 0 || measurement.STopological > 0.25) add("measurement_topological_residual_out_of_domain");
  if (measurement.signedTopologicalPolarization < -1 || measurement.signedTopologicalPolarization > 1) add("g6_polarization_out_of_range");
  if (!Number.isInteger(measurement.refinementCount) || measurement.refinementCount < 1) add("g6_refinement_count_invalid");
  if (!Number.isInteger(measurement.refinedGridSize) || measurement.refinedGridSize < 8) add("g6_refined_grid_size_invalid");
  if (measurement.curvatureErrorEstimateWithSafetyFactor < 0 ||
      measurement.metricAreaErrorEstimateWithSafetyFactor < 0) add("g6_empirical_error_estimate_negative");

  const area = measurement.metricAreaBudget;
  const chern = measurement.chernNumber;
  const floor = Math.abs(chern);
  const positive = measurement.positiveCurvatureBudget;
  const negative = measurement.negativeCurvatureBudget;
  const integrated = measurement.integratedCurvature;
  const saturationRaw = area > 1e-12 ? floor / area : 0;
  const saturation = Math.max(0, Math.min(1, saturationRaw));
  const signedPolarization = Math.sign(chern) * saturation;
  const scalar = (1 - saturation * saturation) / 4;
  const topologicalPositiveProbability = (1 + signedPolarization) / 2;
  const curvatureBudgetTotal = positive + negative;
  const curvatureBudgetPositiveProbability = curvatureBudgetTotal > 1e-12
    ? positive / curvatureBudgetTotal : NaN;
  const expectedEntropyResidual = Math.abs(
    binaryEntropyNats(topologicalPositiveProbability) -
    binaryEntropyNats(curvatureBudgetPositiveProbability)
  );
  const expectedCancellationResidual = Math.abs(
    (area - floor) - 2 * Math.min(positive, negative)
  );
  const expectedVarianceResidual = Math.abs(
    4 * scalar - 4 * (area > 1e-12 ? positive * negative / (area * area) : NaN)
  );
  const identities = [
    ["g6_absolute_curvature_budget_identity_mismatch", measurement.absoluteCurvatureBudget, positive + negative, tolerance],
    ["g6_metric_area_curvature_budget_identity_mismatch", area, measurement.absoluteCurvatureBudget, tolerance],
    ["g6_integrated_curvature_identity_mismatch", integrated, positive - negative, tolerance],
    ["g6_cancellation_budget_identity_mismatch", measurement.curvatureCancellationBudget, Math.max(0, measurement.absoluteCurvatureBudget - Math.abs(integrated)), tolerance],
    ["g6_topological_floor_identity_mismatch", measurement.topologicalFloor, floor, tolerance],
    ["g6_metric_area_excess_identity_mismatch", measurement.metricAreaExcess, area - floor, tolerance],
    ["g6_raw_saturation_identity_mismatch", measurement.topologicalSaturationRaw, saturationRaw, tolerance],
    ["g6_saturation_identity_mismatch", measurement.topologicalSaturation, saturation, tolerance],
    ["g6_signed_polarization_identity_mismatch", measurement.signedTopologicalPolarization, signedPolarization, tolerance],
    ["g6_topological_scalar_identity_mismatch", measurement.STopological, scalar, 1e-12],
    ["g6_psi_identity_mismatch", measurement.psiTopological, CONE + scalar, 1e-12],
    ["g6_accepted_psi_identity_mismatch", measurement.acceptedPsiTopological, measurement.psiTopological, 1e-12],
    ["g6_chern_residual_identity_mismatch", measurement.curvatureChernResidual, Math.abs(integrated - chern), tolerance],
    ["g6_cancellation_residual_identity_mismatch", measurement.curvatureCancellationIdentityResidual, expectedCancellationResidual, 2 * tolerance],
    ["g6_orientation_entropy_identity_mismatch", measurement.curvatureOrientationEntropyResidual, expectedEntropyResidual, 2 * tolerance],
    ["g6_orientation_variance_identity_mismatch", measurement.curvatureOrientationVarianceResidual, expectedVarianceResidual, 2 * tolerance]
  ];
  for (const [code, actual, expected, allowed] of identities) {
    if (!closeEnough(actual, expected, allowed)) add(code);
  }
  if (!closeEnough(measurement.rawChernNumber, chern, Math.max(measurement.chernIntegerResidual, 1e-12))) {
    add("g6_raw_chern_integer_residual_mismatch");
  }
  if (measurement.curvatureChernResidual > tolerance ||
      measurement.curvatureErrorEstimateWithSafetyFactor > tolerance ||
      measurement.metricAreaErrorEstimateWithSafetyFactor > tolerance ||
      measurement.gridAlignmentCurvatureDiscrepancy > tolerance ||
      measurement.gridAlignmentAreaDiscrepancy > tolerance) {
    add("g6_numerical_diagnostic_exceeds_tolerance");
  }
  if (measurement.curvatureCancellationIdentityResidual > 2 * tolerance ||
      measurement.curvatureOrientationEntropyResidual > 2 * tolerance ||
      measurement.metricAreaExcess < -tolerance) {
    add("g6_topological_consistency_diagnostic_exceeds_tolerance");
  }
  return [...new Set(failures)];
}

function normalizeAllowedOrigins(allowedOrigins) {
  if (!Array.isArray(allowedOrigins) || allowedOrigins.length === 0) return null;
  const origins = [];
  for (const value of allowedOrigins) {
    try {
      const parsed = new URL(value);
      if (parsed.protocol !== "https:" || parsed.username || parsed.password ||
          parsed.pathname !== "/" || parsed.search || parsed.hash) return null;
      origins.push(parsed.origin);
    } catch {
      return null;
    }
  }
  return [...new Set(origins)];
}

function validateProofUrl(urlValue, allowedOrigins) {
  const origins = normalizeAllowedOrigins(allowedOrigins);
  if (!origins) return { ok: false, code: "allowed_evidence_origins_missing_or_invalid" };
  try {
    const url = new URL(urlValue);
    if (url.protocol !== "https:" || url.username || url.password || url.search || url.hash ||
        url.href !== urlValue || !origins.includes(url.origin)) {
      return { ok: false, code: "numerical_proof_url_not_pinned_https" };
    }
    return { ok: true, url };
  } catch {
    return { ok: false, code: "numerical_proof_url_invalid" };
  }
}

/**
 * Verify the separate numerical certificate used to promote a QGT diagnostic
 * into G6. The trusted key ID/verifier ID/source SHA/model-input digest and
 * allowed evidence origins must come from deployment configuration, not from
 * the receipt. This verifies the signed certificate and the exact referenced
 * proof bytes; it does not implement the interval-enclosure or analytic-bound
 * method itself. The signing verifier is trusted to have actually established
 * the claimed rigorous bounds.
 */
export function verifyG6NumericalCertification({
  certification,
  proofBytes,
  publicKeyPem = "",
  trustedCertificateKeyId = "",
  trustedVerifierId = "",
  sourceCommitSha = "",
  modelInputDigest = "",
  measurement = null,
  maxQuadratureTolerance = Number(process.env.GREAT_SCALE_G6_MAX_QUADRATURE_TOLERANCE ?? NaN),
  allowedEvidenceOrigins = [],
  now = Date.now(),
  maxAgeMs = 5 * 60 * 1000,
  maxClockSkewMs = 30 * 1000,
} = {}) {
  const failures = [];
  const add = code => failures.push(code);

  // Trusted verification policy inputs must themselves be bounded. An invalid
  // clock/age/skew setting must not silently disable freshness checks.
  if (!Number.isSafeInteger(now) || now < 1) add("verification_clock_invalid");
  if (!Number.isSafeInteger(maxAgeMs) || maxAgeMs < 1 || maxAgeMs > 5 * 60 * 1000) {
    add("numerical_certificate_max_age_policy_invalid");
  }
  if (!Number.isSafeInteger(maxClockSkewMs) || maxClockSkewMs < 0 || maxClockSkewMs > 30 * 1000) {
    add("numerical_certificate_clock_skew_policy_invalid");
  }

  if (!isObject(certification)) {
    return { valid: false, failures: ["numerical_certification_missing_or_malformed"] };
  }
  if (!exactKeys(certification, G6_NUMERICAL_CERTIFICATION_FIELDS)) add("numerical_certification_fields_not_exact");
  if (!G6_NUMERICAL_CERTIFICATE_METHODS.includes(certification.method)) add("numerical_certification_method_invalid");
  if (typeof certification.verifierId !== "string" || !certification.verifierId.trim()) add("numerical_certification_verifier_id_invalid");
  if (!trustedVerifierId || certification.verifierId !== trustedVerifierId) add("numerical_certification_verifier_id_mismatch");
  if (!trustedCertificateKeyId || certification.certificateKeyId !== trustedCertificateKeyId) add("numerical_certificate_key_id_mismatch");
  if (certification.verified !== true) add("numerical_certification_not_verified");
  if (typeof sourceCommitSha !== "string" || !FULL_SHA.test(sourceCommitSha) ||
      certification.sourceCommitSha !== sourceCommitSha || !FULL_SHA.test(certification.sourceCommitSha || "")) {
    add("numerical_certification_source_commit_mismatch");
  }
  if (typeof modelInputDigest !== "string" || !SHA256_HEX.test(modelInputDigest) ||
      certification.modelInputDigest !== modelInputDigest || !SHA256_HEX.test(certification.modelInputDigest || "")) {
    add("numerical_certification_model_input_digest_mismatch");
  }
  if (!isObject(measurement)) {
    add("measurement_missing_for_numerical_certification");
  } else {
    for (const failure of validateG6Measurement(measurement, maxQuadratureTolerance)) add(failure);
    const tolerance = measurement.quadratureTolerance;
    if (typeof tolerance !== "number" || !Number.isFinite(tolerance) || tolerance <= 0) {
      add("measurement_quadrature_tolerance_invalid");
    }
    let expectedMeasurementDigest = null;
    try {
      expectedMeasurementDigest = sha256Hex(canonicalG6CertificateJson(measurement));
    } catch {
      add("measurement_not_canonicalizable");
    }
    if (!SHA256_HEX.test(certification.measurementDigest || "") ||
        expectedMeasurementDigest === null ||
        certification.measurementDigest !== expectedMeasurementDigest) {
      add("numerical_certification_measurement_digest_mismatch");
    }
    if (typeof certification.curvatureErrorUpperBound !== "number" ||
        !Number.isFinite(certification.curvatureErrorUpperBound) || certification.curvatureErrorUpperBound < 0 ||
        !(typeof tolerance === "number" && Number.isFinite(tolerance)) ||
        certification.curvatureErrorUpperBound > tolerance) {
      add("certified_curvature_error_exceeds_tolerance_or_invalid");
    }
    if (typeof certification.metricAreaErrorUpperBound !== "number" ||
        !Number.isFinite(certification.metricAreaErrorUpperBound) || certification.metricAreaErrorUpperBound < 0 ||
        !(typeof tolerance === "number" && Number.isFinite(tolerance)) ||
        certification.metricAreaErrorUpperBound > tolerance) {
      add("certified_metric_area_error_exceeds_tolerance_or_invalid");
    }
  }
  const urlCheck = validateProofUrl(certification.evidenceUrl, allowedEvidenceOrigins);
  if (!urlCheck.ok) add(urlCheck.code);
  if (!SHA256_HEX.test(certification.proofDigest || "")) add("numerical_proof_digest_invalid");

  const generated = validTimestamp(certification.generatedAt) ? Date.parse(certification.generatedAt) : NaN;
  const expires = validTimestamp(certification.expiresAt) ? Date.parse(certification.expiresAt) : NaN;
  if (!Number.isFinite(generated) || !Number.isFinite(expires)) {
    add("numerical_certificate_timestamps_invalid");
  } else {
    if (generated > now + maxClockSkewMs) add("numerical_certificate_generated_in_future");
    if (now - generated > maxAgeMs) add("numerical_certificate_stale");
    if (expires <= now) add("numerical_certificate_expired");
    if (expires <= generated || expires - generated > maxAgeMs) add("numerical_certificate_lifetime_invalid");
  }

  if (!(proofBytes instanceof Uint8Array)) {
    add("numerical_proof_bytes_missing");
  } else {
    if (sha256Hex(Buffer.from(proofBytes)) !== certification.proofDigest) add("numerical_proof_digest_mismatch");
    let proof;
    try {
      proof = JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(proofBytes));
    } catch {
      add("numerical_proof_json_invalid");
    }
    if (proof !== undefined) {
      if (!exactKeys(proof, PROOF_FIELDS)) add("numerical_proof_fields_not_exact");
      if (proof.schema !== G6_NUMERICAL_CERTIFICATE_SCHEMA) add("numerical_proof_schema_mismatch");
      for (const key of [
        "method", "verifierId", "sourceCommitSha", "modelInputDigest", "measurementDigest",
        "curvatureErrorUpperBound", "metricAreaErrorUpperBound", "generatedAt", "expiresAt"
      ]) {
        if (proof[key] !== certification[key]) add("numerical_proof_" + key + "_mismatch");
      }
      if (!isObject(proof.witness) || Object.keys(proof.witness).length === 0) {
        add("numerical_proof_witness_missing");
      }
    }
  }

  const { certificateSignature, ...unsignedCertificate } = certification;
  if (!publicKeyPem || !trustedCertificateKeyId || !trustedVerifierId) {
    add("numerical_certificate_trust_configuration_missing");
  } else if (typeof certificateSignature !== "string" || !ED25519_SIGNATURE.test(certificateSignature)) {
    add("numerical_certificate_signature_malformed");
  } else {
    try {
      const publicKey = createPublicKey(publicKeyPem);
      const signatureBytes = Buffer.from(certificateSignature, "base64");
      if (publicKey.asymmetricKeyType !== "ed25519") {
        add("numerical_certificate_public_key_type_invalid");
      } else if (signatureBytes.length !== 64 ||
          signatureBytes.toString("base64") !== certificateSignature ||
          !verifySignature(null, Buffer.from(canonicalG6CertificateJson(unsignedCertificate), "utf8"),
            publicKey, signatureBytes)) {
        add("numerical_certificate_signature_invalid");
      }
    } catch {
      add("numerical_certificate_key_or_signature_invalid");
    }
  }

  return {
    valid: failures.length === 0,
    failures,
    certificate: failures.length === 0 ? {
      method: certification.method,
      verifierId: certification.verifierId,
      sourceCommitSha: certification.sourceCommitSha,
      modelInputDigest: certification.modelInputDigest,
      measurementDigest: certification.measurementDigest,
      curvatureErrorUpperBound: certification.curvatureErrorUpperBound,
      metricAreaErrorUpperBound: certification.metricAreaErrorUpperBound,
      proofDigest: certification.proofDigest,
      generatedAt: certification.generatedAt,
      expiresAt: certification.expiresAt
    } : null
  };
}

/**
 * Fetch a numerical proof artifact from a deployment-pinned HTTPS origin.
 * Redirects are refused and the exact requested URL is required on response.
 */
export async function fetchG6NumericalProofBytes({
  url,
  allowedEvidenceOrigins = [],
  fetchImpl = globalThis.fetch,
  timeoutMs = DEFAULT_TIMEOUT_MS,
  maxBytes = DEFAULT_MAX_BYTES
} = {}) {
  const urlCheck = validateProofUrl(url, allowedEvidenceOrigins);
  if (!urlCheck.ok) return { valid: false, failures: [urlCheck.code] };
  if (typeof fetchImpl !== "function") return { valid: false, failures: ["fetch_unavailable"] };
  if (!Number.isSafeInteger(timeoutMs) || timeoutMs < 1 || timeoutMs > 10_000) {
    return { valid: false, failures: ["timeout_limit_invalid"] };
  }
  if (!Number.isSafeInteger(maxBytes) || maxBytes < 1 || maxBytes > HARD_MAX_BYTES) {
    return { valid: false, failures: ["proof_size_limit_invalid"] };
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetchImpl(urlCheck.url.href, {
      method: "GET",
      redirect: "error",
      cache: "no-store",
      headers: { accept: "application/json", "cache-control": "no-cache" },
      signal: controller.signal
    });
    if (!response || response.status !== 200 || response.ok !== true ||
        response.redirected === true || response.url !== urlCheck.url.href) {
      try { await response?.body?.cancel(); } catch {}
      return { valid: false, failures: ["numerical_proof_response_identity_invalid"] };
    }
    const contentType = (response.headers?.get("content-type") || "")
      .split(";", 1)[0].trim().toLowerCase();
    if (contentType !== "application/json") {
      try { await response.body?.cancel(); } catch {}
      return { valid: false, failures: ["numerical_proof_content_type_invalid"] };
    }
    const lengthHeader = response.headers?.get("content-length");
    if (lengthHeader !== null && lengthHeader !== undefined &&
        (!/^\d+$/.test(lengthHeader) || Number(lengthHeader) > maxBytes)) {
      try { await response.body?.cancel(); } catch {}
      return { valid: false, failures: ["numerical_proof_content_length_invalid"] };
    }
    if (!response.body || typeof response.body.getReader !== "function") {
      return { valid: false, failures: ["numerical_proof_stream_unavailable"] };
    }
    const reader = response.body.getReader();
    const chunks = [];
    let size = 0;
    try {
      while (true) {
        const entry = await reader.read();
        if (entry.done) break;
        if (!(entry.value instanceof Uint8Array)) {
          try { await reader.cancel(); } catch {}
          return { valid: false, failures: ["numerical_proof_chunk_invalid"] };
        }
        size += entry.value.byteLength;
        if (size > maxBytes) {
          try { controller.abort(); } catch {}
          try { await reader.cancel(); } catch {}
          return { valid: false, failures: ["numerical_proof_body_too_large"] };
        }
        chunks.push(Buffer.from(entry.value));
      }
    } finally {
      try { reader.releaseLock(); } catch {}
    }
    return { valid: true, bytes: Buffer.concat(chunks, size), url: urlCheck.url.href };
  } catch {
    try { controller.abort(); } catch {}
    return { valid: false, failures: ["numerical_proof_fetch_failed"] };
  } finally {
    clearTimeout(timeout);
  }
}

export async function fetchAndVerifyG6NumericalCertification(options = {}) {
  const certification = options.certification;
  const fetched = await fetchG6NumericalProofBytes({
    url: certification?.evidenceUrl,
    allowedEvidenceOrigins: options.allowedEvidenceOrigins,
    fetchImpl: options.fetchImpl,
    timeoutMs: options.timeoutMs,
    maxBytes: options.maxBytes
  });
  if (!fetched.valid) return { valid: false, failures: fetched.failures, certificate: null };
  return verifyG6NumericalCertification({ ...options, proofBytes: fetched.bytes });
}
