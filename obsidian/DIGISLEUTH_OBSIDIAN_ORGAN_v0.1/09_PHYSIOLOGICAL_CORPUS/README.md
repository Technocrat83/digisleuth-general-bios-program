---
id: DS_PHYSIOLOGICAL_RELATIONSHIP_CORPUS_v0.1
schema: DS_OBSIDIAN_PHYSIOLOGICAL_CRYSTAL_v1
class: PHYSIOLOGICAL_RELATIONSHIP_CORPUS
standing: REPRESENTATIONAL_ONLY
admission_authority: GOVERNANCE_KERNEL
projection_surface: OBSIDIAN
source_of_lineage: GIT
---

# PHYSIOLOGICAL RELATIONSHIP CORPUS

## Purpose

This surface projects graph-native physiological relationships among Digisleuth phenotypes, organs, habitats, pressures, dependencies, and coupling evidence.

## Governing laws

- Phenotypes are nodes; physiology is relational; runtime evidence weights the edges.
- Graph topology may suggest ecological possibility, but demonstrated pressure and governed evidence establish physiological standing.
- Graph Gap != Physiological Necessity != Phenotype Admission.
- Automated Writing != Automated Authority.

## Serialization rule

Every graph-bearing entity MUST be a `.md` file. Typed relationships intended to appear in Obsidian Graph MUST be encoded as quoted Obsidian internal links, for example:

```yaml
depends_on:
  - "[[GOVERNANCE_KERNEL]]"
```

Folder location carries no semantic authority.

## Authority boundary

This corpus may project, compare, and expose relationships. It may not confer scientific standing, phenotype admission, execution authority, or constitutional mutation.

## Federation spine

`Airtable -> Git -> OpenAI -> Obsidian`

Airtable supplies operational registry state. Git preserves authenticated lineage and residue. OpenAI may derive candidate relationships without conferring standing. Obsidian projects the ecological topology. Governance retains admission and mutation authority.
