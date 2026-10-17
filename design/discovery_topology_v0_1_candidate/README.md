---
artifact_id: DIGISLEUTH_DISCOVERY_TOPOLOGY_v0.1_candidate
standing: DESIGN_CANDIDATE
authority_effect: NONE
production_enforcement: NOT_EVALUATED
commercial_release: HOLD
---

# Digisleuth discovery topology

“Digisleuth provides Discovery to its Topology with curiosity as the tension gradient.” — Founder direction, 2026-10-17.

## Outcome and scope
This candidate expands the publishing/Living Funnel design into a typed graph, standalone Obsidian review vault, nested Canvas and Figma handoff. It defines new candidate identities; it does not claim to extract, admit or promote existing corpus relationships. No live visitor events or UA export are present. No website, live vault, production pointer or Figma file is changed by these files.

## Three graphs and one correspondence map
1. Semantic graph: what subjects, publications, questions, claims and evidence mean and how they relate. Stable object IDs survive URL and layout changes.
2. Navigation graph: routes offered by a particular published interface revision, including visibility, prerequisites, explicit choice, backtracking and exit. Availability is not traversal or permission.
3. Observation graph: events that actually occurred, with source revision, collection window and missingness. Co-visitation never becomes a semantic edge automatically.
A versioned correspondence map joins these graphs through IDs without conflating their relationship types. States, transitions and authorities remain separate collections.

## Nested Obsidian representation
The standalone review vault is in review_vault/. Outer container = candidate topology; inner containers = semantic, navigation and behavior layers. The semantic layer contains a silo group and its publication/question/evidence notes. A typed relationship record lives in each source note, with full-path wikilinks for navigation. Canvas edges use PROPOSED plus their exact predicate. Native graph adjacency is a navigation affordance; typed JSON and note records retain the predicate semantics. Graph layout distance is not semantic distance. This is a proposed extension, not a ratified DS_OBSIDIAN_PHYSIOLOGICAL_CRYSTAL_v1 schema migration.

## Curiosity gradient: hypothesis and operationalization
Let q be a visitor's explicitly selected question and n the current node. A candidate relevance function U(q,n) could estimate how useful n is for answering q. A discrete difference U(q,next)-U(q,current) can describe a proposed direction for discovery; no values, weights or validated psychometric interpretation exist here. Show relevant adjacent choices with reasons and let the visitor choose. Record declared interest separately from clicks, dwell or scrolling. Do not infer trust, identity, consent, urgency or readiness from passive behavior. Never manufacture uncertainty or withhold the answer to increase traversal.

## Attention basins
An attention basin is a time-bounded assessment of observed concentration in a defined subgraph, with membership rule, exposure denominator, bot/session policy, exclusions, sample size, source version and uncertainty. Zero observations means UNESTABLISHED, not zero interest. Display counts, offered-route exposure, selection rates, return paths and exits separately. A heat overlay must distinguish missing data from measured zero. No production heatmap or empirical basin is asserted in this candidate.

## Git / Understand Anything integration
Pinned Git source -> preserved raw UA export -> candidate identity reconciliation -> independent endpoint AND relationship adjudication -> admitted graph -> projection manifest -> Obsidian/Figma/website views.
UA supplies candidates only. It does not collect browser behavior or decide meaning. Behavioral observations enter through a separate versioned ingestion path. Bind raw export SHA-256, installed UA revision/package digest, executed configuration SHA-256, source commit and review receipts before claiming actual UA integration. No downstream renderer repairs missing source facts. Preserve rejected/unresolved outcomes. Current candidate has real UA admissions 0.

## Figma surface contract
Import figma_handoff.json as a design specification, not a claim that Figma has been populated. Frames follow layer/silo containment; cards retain source IDs and standing. Connector label and direction must match topology.json. Outline/badge = standing; containment = declared grouping; node size = fixed default unless an explicitly selected metric is available; heat = observed metric only, with window and denominator; dashed route = proposed navigation. Layout edits are presentation-only. Meaning/edge edits create petitions for source review. Figma coordinates never confer admission, centrality, jurisdiction or authority. Reconcile source graph digest and all node/edge mappings after any export/import.

## Publishing and URLs
Public URLs identify stable topic resources. Browser/session state stays separate from semantic identity. Keep source lineage distinct from SEO canonicalization: a materially different application may be derived from an article without being a duplicate. Every public representation keeps claims and qualifications faithful to the bound source. Nested silos may have cross-silo relationships; folders do not prohibit links. The URL paths in this candidate are proposals, not verified live pages.

## Governance and deployment
MAGUS orients and presents allowed relationships. HCE represents; BMIMS checks conformance. None gains promotion authority. Behavior may propose editorial changes but does not rewrite source meaning. Inquiry does not activate an engagement or grant production execution authority. This candidate is staged outside the managed Obsidian Organ and does not alter its active manifest. A later live projection requires the actual destination/tool binding, exact-byte write plan, valid scoped grant, concurrency controls, readback and activation receipt described by the existing jurisdiction architecture.

## Acceptance and remaining work
Local validation checks IDs, full edge records, note links, Canvas structure, mapped Figma identities, absence of fabricated observations and artifact hashes. These checks establish structural fidelity of this authored candidate only. Real extraction, independent semantic adjudication, telemetry calibration, Figma rendering, Obsidian application rendering and runtime enforcement remain unevaluated.

## Source references
- Current Founder request and preceding publishing architecture proposal, 2026-10-17.
- Repository branch general-bios-laboratory-v1 at b194dd3fe745350f870a63a2f139e170dcb8f530.
- .agents/skills/json-canvas/SKILL.md and DIGISLEUTH_BINDING.md, read at that revision.
- obsidian/DIGISLEUTH_OBSIDIAN_ORGAN_v0.1/REMOTE_WRITE_POLICY.md and CANVAS_SKILL_BINDING.md.
- Existing MAGUS.md in 09_PHYSIOLOGICAL_CORPUS/01_PHENOTYPES, inspected without changing its standing.
- DOSSIER_UA_OBSIDIAN_JURISDICTION_FUNCTION_ARCHITECTURE_v0.1.md, current saved source read 2026-10-17. This candidate does not claim conformance to an unbound Dossier schema.
