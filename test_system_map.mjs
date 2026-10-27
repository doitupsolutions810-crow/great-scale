import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { validateRepositoryMap } from "./tools/validate-repository-map.mjs";

const baseline = JSON.parse(readFileSync(new URL("./integration/repository-map.json", import.meta.url), "utf8"));

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

test("a repository cannot be marked verified without exact-head execution evidence", () => {
  const candidate = structuredClone(baseline);
  candidate.repositories[0].integrationStatus = "verified";
  assert.ok(validateRepositoryMap(candidate).some((message) => message.includes("cannot be marked verified without a full commit SHA")));
});

test("an interface cannot be marked verified without receipt-grade evidence", () => {
  const candidate = structuredClone(baseline);
  candidate.interfaces[0].verificationStatus = "verified";
  assert.ok(validateRepositoryMap(candidate).some((message) => message.includes("cannot be marked verified without commit SHA")));
});
