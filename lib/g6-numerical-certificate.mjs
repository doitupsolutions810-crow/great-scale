import { createHash, createPublicKey, verify as verifySignature } from "node:crypto";

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

const CERTIFICATE_FIELDS = Object.freeze([
  "method", "verifierId", "sourceCommitSha", "modelInputDigest", "measurementDigest",
  "curvatureErrorUpperBound", "metricAreaErrorUpperBound", "evidenceUrl", "proofDigest",
  "verified", "certificateKeyId", "certificateSignature", "generatedAt", "expiresAt"
]);
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
  if (!exactKeys(certification, CERTIFICATE_FIELDS)) add("numerical_certification_fields_not_exact");
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
    const tolerance = measurement.quadratureTolerance;
    if (typeof tolerance !== "number" || !Number.isFinite(tolerance) || tolerance <= 0) {
      add("measurement_quadrature_tolerance_invalid");
    }
    const residualS = measurement.STopological;
    if (typeof residualS !== "number" || !Number.isFinite(residualS) ||
        residualS < 0 || residualS > 0.25) {
      add("measurement_topological_residual_out_of_domain");
    }
    if (measurement.topologicalMappingValid !== true) {
      add("measurement_topological_mapping_invalid");
    }
    if (measurement.quadratureConverged !== true) {
      add("measurement_quadrature_not_converged");
    }
    if (measurement.errorEstimatesFinite !== true) {
      add("measurement_empirical_estimates_not_finite");
    }
    if (measurement.errorBoundMethod !== "richardson-asymptotic-estimate-only") {
      add("measurement_empirical_error_method_mismatch");
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
