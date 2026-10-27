# Great Scale CXLXXII — Representation Invariance

## Question
If a finite model is renamed by bijections over state labels and action labels, while observations, properties, and transition structure are preserved, should its quotient change?

## Formal statement
Let rho be a bijective renaming of state and action labels that preserves observations, properties, terminal edges, and transition incidence. Then the quotient partitions should correspond under rho:

`Q(rho(M)) = rho(Q(M))`.

Equality is understood as mapped equivalence classes, not equality of raw canonical IDs. Canonical IDs necessarily change when labels change.

## Tests authored
- Rename all state labels and action labels and compare quotient blocks after mapping the original blocks through the state-label bijection.
- Repeat with typed Boolean/integer observations to ensure representation invariance does not erase typed semantic distinctions.

## Scientific significance
This is a metamorphic property: it tests a relationship between multiple executions without requiring a separate expected partition for every model. It can expose accidental dependence on the spelling or representation of labels.

## Limits and status
Tests are authored but not independently executed here. The property covers bijective renaming only; it does not establish invariance under arbitrary transformations, non-bijective mappings, or changes to observations and properties.