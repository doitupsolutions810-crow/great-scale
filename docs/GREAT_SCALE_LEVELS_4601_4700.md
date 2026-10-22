# Great Scale Levels 4601–4700 — Semantic fidelity at the representation boundary

## Finding

A further audit found that the public propositional evaluator used JavaScript truthiness and ordinary property lookup for atoms. That is not identical to a logical valuation. In JavaScript, a missing key such as `toString` can resolve to an inherited property, and a string such as `"false"` is truthy despite not being the Boolean value false.

The evaluator now requires:
- an object-like valuation environment (not null or an array);
- an explicit own-property assignment for every atom evaluated;
- a Boolean value for every assignment.

The regression suite now checks inherited-property lookup, missing assignments, string-valued assignments, valid true/false assignments, cyclic formula/proof structures, and an oversized proof-object schema.

## Mathematics

A valuation is a total function (
u:mathsf{Atom}	omathbb B), where (mathbb B={ot,	op}). Formula semantics are defined recursively:

[
egin{aligned}
llbracket prbracket_
u &= 
u(p),\
llbracket Aland Brbracket_
u &= llbracket Arbracket_
ulandllbracket Brbracket_
u,\
llbracket Alor Brbracket_
u &= llbracket Arbracket_
ulorllbracket Brbracket_
u,\
llbracket A	o Brbracket_
u &= 
egllbracket Arbracket_
ulorllbracket Brbracket_
u.
end{aligned}
]

Ordinary object lookup is not a valid implementation of (
u) unless missing keys, inherited properties, and value types are controlled. Otherwise the program evaluates a different semantics from the one named by the mathematical specification.

## Executed reference checks

A targeted JavaScript reference harness passed **10/10 checks** after these changes:
1. shared aggregate budget rejects nested `orIR` formula-budget resets;
2. truth-table work budget rejects an adversarial full valuation workload;
3. the stress fixture itself stays within configured input bounds;
4. atom and rule-label length limits reject oversized values;
5. valid small assumptions and tautologies remain accepted;
6. valuations require own Boolean properties and reject inherited/missing/string/null/array cases;
7. cyclic formula ASTs fail closed at the depth bound;
8. cyclic proof objects fail closed at the depth bound;
9. very wide proof objects fail closed at the schema-size gate;
10. a valid generated truth-table tautology remains accepted.

These are reference tests of equivalent logic executed in the available JavaScript tool environment. They are not evidence that the complete repository `npm test` command has run.

## Runner integration

The latest GitHub Actions run still fails without step or log metadata. Cross-repository inspection found:
- `swarm-vm-runner` explicitly documents the hosted `runner_id 0` failure and recommends a self-hosted runner;
- its current runner defaults to the separate `control12-workspace` repository, requires a repository-scoped registration token, and mounts the Docker socket;
- `capability-authority/docs/CI.md` lists an account-level billing lock as a possible cause, but the current Great Scale job does not expose that exact diagnostic.

A dedicated, isolated runner must be registered to Great Scale or the account-level hosted-runner issue must be resolved. Reusing a Docker-socket-enabled runner for arbitrary pull-request code is not an acceptable shortcut. See `docs/CI_RUNNER_RECOVERY.md`.

## Great Scale candidate principle

**Verification requires representation fidelity as well as inference correctness.** The encoded input must denote the intended mathematical object, and each operation must preserve that meaning. Resource bounds protect execution; typed valuation semantics protect what the execution means.

This is a formal-methods and software-assurance conclusion. It does not establish a physical quantum-geometry law.
