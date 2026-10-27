#!/usr/bin/env node
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";

const allowedRoleEvidence = new Set(["readme-inspected", "inventory-only"]);
const allowedIntegrationStatus = new Set(["not-end-to-end-verified", "not-inspected", "blocked", "verified"]);
const allowedInterfaceStatus = new Set(["proposed-not-verified", "blocked", "verified"]);
const shaPattern = /^[a-f0-9]{40}$/i;

export function validateRepositoryMap(map) {
  const errors = [];
  const add = (message) => errors.push(message);
  if (!map || typeof map !== "object" || Array.isArray(map)) {
    return ["map must be an object"];
  }
  if (map.schemaVersion !== 1) add("schemaVersion must equal 1");
  if (map.scope !== "public-only") add("public registry scope must be public-only");
  if (!map.operationEvidenceContract || map.operationEvidenceContract.version !== "v1" || map.operationEvidenceContract.path !== "docs/OPERATION_EVIDENCE_CONTRACT_V1.md" || map.operationEvidenceContract.status !== "proposed") add("operationEvidenceContract must bind the proposed v1 contract document");
  if (typeof map.owner !== "string" || !map.owner.trim()) add("owner must be a non-empty string");
  if (typeof map.inventoryAsOf !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(map.inventoryAsOf)) add("inventoryAsOf must be YYYY-MM-DD");
  if (!Number.isInteger(map.expectedRepositoryCount) || map.expectedRepositoryCount < 1) add("expectedRepositoryCount must be a positive integer");
  if (!Array.isArray(map.repositories)) {
    add("repositories must be an array");
    return errors;
  }
  if (map.expectedRepositoryCount !== map.repositories.length) {
    add(`repository count mismatch: expected ${map.expectedRepositoryCount}, got ${map.repositories.length}`);
  }
  const names = new Set();
  for (const [index, repo] of map.repositories.entries()) {
    const prefix = `repositories[${index}]`;
    if (!repo || typeof repo !== "object" || Array.isArray(repo)) {
      add(`${prefix} must be an object`);
      continue;
    }
    if (typeof repo.name !== "string" || !repo.name.trim() || repo.name.includes("/")) {
      add(`${prefix}.name must be a non-empty repository name without a slash`);
    } else if (names.has(repo.name)) {
      add(`duplicate repository name: ${repo.name}`);
    } else {
      names.add(repo.name);
    }
    if (repo.owner !== map.owner) add(`${prefix}.owner must equal map.owner`);
    if (!["public", "private"].includes(repo.visibility)) add(`${prefix}.visibility must be public or private`);
    if (map.scope === "public-only" && repo.visibility !== "public") add(`${prefix}.visibility must be public in a public-only registry`);
    if (typeof repo.defaultBranch !== "string" || !repo.defaultBranch.trim()) add(`${prefix}.defaultBranch must be non-empty`);
    if (typeof repo.role !== "string" || !repo.role.trim()) add(`${prefix}.role must be non-empty`);
    if (!allowedRoleEvidence.has(repo.roleEvidence)) add(`${prefix}.roleEvidence is not recognized`);
    if (!allowedIntegrationStatus.has(repo.integrationStatus)) add(`${prefix}.integrationStatus is not recognized`);
    if (typeof repo.note !== "string" || !repo.note.trim()) add(`${prefix}.note must state the evidence or uncertainty`);
    if (repo.integrationStatus === "verified") {
      const proof = repo.verification;
      if (!proof || !shaPattern.test(proof.commitSha ?? "") || !proof.testRunUrl || !proof.observedResult) {
        add(`${prefix} cannot be marked verified without a full commit SHA, test-run URL, and observed result`);
      }
    }
  }
  if (!Array.isArray(map.interfaces)) {
    add("interfaces must be an array");
    return errors;
  }
  const edgeKeys = new Set();
  for (const [index, edge] of map.interfaces.entries()) {
    const prefix = `interfaces[${index}]`;
    if (!edge || typeof edge !== "object" || Array.isArray(edge)) {
      add(`${prefix} must be an object`);
      continue;
    }
    if (!names.has(edge.from)) add(`${prefix}.from references an unknown repository: ${edge.from}`);
    if (!names.has(edge.to)) add(`${prefix}.to references an unknown repository: ${edge.to}`);
    if (edge.from === edge.to) add(`${prefix} must connect two different repositories`);
    if (typeof edge.contract !== "string" || !edge.contract.trim()) add(`${prefix}.contract must be non-empty`);
    if (!allowedInterfaceStatus.has(edge.verificationStatus)) add(`${prefix}.verificationStatus is not recognized`);
    if (!Array.isArray(edge.requiredEvidence) || edge.requiredEvidence.length === 0) add(`${prefix}.requiredEvidence must be a non-empty array`);
    const key = `${edge.from} -> ${edge.to}`;
    if (edgeKeys.has(key)) add(`duplicate interface: ${key}`);
    edgeKeys.add(key);
    if (edge.verificationStatus === "verified") {
      const proof = edge.verification;
      if (!proof || !shaPattern.test(proof.commitSha ?? "") || !proof.testRunUrl || !proof.observedResult || !proof.evidenceUrl) {
        add(`${prefix} cannot be marked verified without commit SHA, test-run URL, observed result, and evidence URL`);
      }
    }
  }
  return errors;
}

function run() {
  const manifestPath = resolve(process.argv[2] ?? "integration/repository-map.json");
  let map;
  try {
    map = JSON.parse(readFileSync(manifestPath, "utf8"));
  } catch (error) {
    console.error(`FAIL: cannot read valid JSON at ${manifestPath}: ${error.message}`);
    process.exitCode = 1;
    return;
  }
  const errors = validateRepositoryMap(map);
  if (errors.length) {
    console.error(`FAIL: repository map has ${errors.length} issue(s):`);
    for (const error of errors) console.error(`- ${error}`);
    process.exitCode = 1;
    return;
  }
  console.log(`PASS: repository map is structurally valid (${map.repositories.length} repositories, ${map.interfaces.length} proposed interfaces).`);
  console.log("NOTE: structural validity does not mean repository interfaces or runtime behavior are end-to-end verified.");
}

if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) run();
