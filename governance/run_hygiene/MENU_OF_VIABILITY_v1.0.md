# Menu of Viability — Run Hygiene Operation v1.0

**Canonical ID:** `MENU_OF_VIABILITY_RUN_HYGIENE_OPERATION_v1.0`  
**Display name:** Menu of Viability  
**Classification:** Founder decision support / Run Hygiene / Commercial projection  
**Standing:** CANONICAL_OPERATIONAL_WORKFLOW — FOUNDER_AUTHORIZED  
**Authority source:** Explicit Founder directive in this conversation, 2026-10-28  
**Canonical scope:** Company-level operational workflow  
**Registry:** [Run Hygiene Canon registry](RUN_HYGIENE_CANON_REGISTRY_v1.json)

## Founder definition

> A Menu of Viability is a Run Hygiene Operation which projects a line of best fit of commercial offerings of an architectural candidate so that Founder may pinpoint and isolate features and overall assess allocation of resources

The same directive explicitly states: “I want this workflow to enter Canon.”

This artifact records that operational convention. Its canonical status does not assert that any architectural candidate, commercial offering, market-demand hypothesis, or scientific proposition has been validated.

## Purpose

Project an architectural candidate into a reviewable menu of possible commercial offerings. Make the contributing features, dependencies, claim limits, evidence gaps, and resource implications explicit so that Founder can pinpoint features, isolate a bounded offering, compare development paths, and assess allocation of resources.

The menu is a decision surface. Founder retains selection, prioritization, and allocation authority.

## Meaning of “line of best fit”

A line of best fit is the declared, reasoned correspondence:

**candidate capability → feature → buyer problem → bounded offering → evidence needed → resource implications**

The projection explains why each proposed offering fits the candidate and what would have to become true to make it deliverable and valuable.

The default output is qualitative and multidimensional. No undeclared score, weight, revenue estimate, ranking heuristic, or statistical regression is implied. Where a numerical fitting or aggregation method is used, name its data, assumptions, uncertainty, method, and separately accepted decision rule. Preserve the unaggregated dimensions for Founder inspection.

A feature may be commercially interesting while its delivery readiness, scientific standing, demand evidence, or resource estimate remains unknown. Unknowns remain visible.

## Invocation

Invoke **Menu of Viability** during Run Hygiene when an architectural candidate is considered for commercial development, feature isolation, or resource allocation.

Inputs:

1. Candidate identifier, exact version/commit, source paths, and current standing.
2. Demonstrated, implemented-but-unvalidated, and proposed capabilities, distinguished explicitly.
3. Known architectural dependencies, authority constraints, and claim ceiling.
4. Founder-supplied buyer context, objectives, or resource envelope, when available; absent inputs remain unknown.

Refresh a menu when its candidate revision, evidence, dependencies, buyer context, or Founder resource envelope materially changes. A refresh creates a new version and preserves the prior projection.

This workflow definition creates no scheduled task or automatic execution.

## Required operation

1. **Bind identity.** Record the architectural candidate and source revision. Preserve its current scientific, implementation, and authority states.
2. **Run hygiene.** Separate observed capability, design proposal, inference, and commercial hypothesis. Surface contradictions and unsupported claims.
3. **Decompose features.** Give features stable IDs. Record dependencies and whether each feature can be isolated, is coupled, or has unknown separability.
4. **Project offerings.** Map features to buyer problems and the smallest bounded purchasable embodiment that can be coherently proposed. Describe the commercial fit and its assumptions.
5. **Expose viability conditions.** Record delivery gaps, evidence required, operating constraints, and what would defeat the commercial hypothesis.
6. **Expose resources.** Distinguish build, validation, integration, delivery, and ongoing support work. Record time/cost estimates only with a stated basis; leave unbound estimates unknown.
7. **Return the menu.** Present feature-level and offering-level comparisons, unresolved dependencies, and possible next information-gathering actions.
8. **Return decision authority to Founder.** Record any subsequent Founder selection or allocation as a distinct decision with its scope and provenance.

If no defensible offering can be projected, return `NO_CURRENT_MARKET_OBJECT` with reasons. Do not force a market object or an allocation recommendation.

## Required output contract

Every menu must include:

| Field | Required content |
|---|---|
| Menu identity | Menu ID, version, date, operation version, and predecessor when applicable. |
| Candidate binding | Candidate ID, source revision, source path(s), and present standing. |
| Claim ceiling | Demonstrated capability, uncertainty, prohibited claims, and authority limits. |
| Feature catalog | Feature IDs, descriptions, maturity, dependencies, separability, and proof needed. |
| Proposed offerings | Offering IDs, buyer/problem hypotheses, bounded deliverable, contributing feature IDs, and fit rationale. |
| Viability conditions | Evidence needed, delivery gaps, falsifiers, and unresolved assumptions. |
| Resource implications | Build, validation, integration, delivery/support work, estimate basis, and known/unknown time and cost. |
| Overall comparison | Explicit tradeoffs and dependencies across offerings; preserve multiple fit dimensions. |
| Founder isolation surface | Features that could be selected, retained, deferred, or investigated, with coupling limits. |
| Founder decision record | Actual decisions only; `[]` when none has been made. |
| Next information object | A scoped action proposal that would reduce a named uncertainty; authorization remains separate. |
| Outcome | `MENU_PROJECTED` or `NO_CURRENT_MARKET_OBJECT`. |

The menu may present several ways to package the same feature. It must expose shared dependencies and avoid counting a shared capability or shared resource requirement as independent in each offering.

## Hygiene rules

- A proposed customer benefit is a hypothesis until supported by customer-outcome evidence.
- Architectural plausibility, buyer interest, purchase commitment, payment, and repeat purchase are distinct states.
- Commercial fit does not upgrade scientific standing or relax an architectural constraint.
- A feature's commercial attractiveness does not establish that it is technically separable.
- A resource estimate must identify its basis and uncertainty. Unknown effort is not zero effort.
- Projection, comparison, Founder selection, allocation, admission, execution, and publication are separate events.
- A menu cannot authorize its own next action, spend, experiment, commercialization, or promotion.
- Preserve provenance and revision history. No favorable rewriting of prior menus after outcomes.
- The output is reviewable even when demand, pricing, effort, or evidence remains unknown.

## Authority and Canon boundary

Founder’s present directive canonizes this **operational workflow**. It does not canonize the originating AVIV architectural candidate.

| Surface | Effect of this artifact |
|---|---|
| Operational Canon | Adds Menu of Viability as a Founder-authorized Run Hygiene convention. |
| Scientific standing / scientific Canon | No change. |
| Architectural candidate or apparatus admission | No change. |
| Experimental execution, resource commitment, production promotion | No grant. |
| Founder feature selection and resource allocation | Remains with Founder; requires a separately recorded decision. |

The operation produces commercial projections and supporting structure. It has no authority to issue scientific ratification or to substitute commercial desirability for General BIOS Theorem adjudication.

This is compatible with the frozen Nexus distinction between evaluation, selection, admission, and execution. It introduces no undeclared scalarization and does not modify the Nexus protocol.

## First recorded application

[AVIV governed-state-stabilization menu](examples/MENU_OF_VIABILITY_AVIV_GSS_v0.1.json) preserves the eight previously proposed utility features and demonstrates possible offering groupings.

Its source candidate remains untested in draft PR #9. The example records commercial hypotheses, unknown resource quantities, and no Founder allocation decision. It is an operational projection, not an empirical result or a live offering.

## Maintenance

The definition is versioned. A change to the operation's purpose, required fields, authority boundary, or fitting method requires a new operational version and explicit Founder approval. The operation cannot amend itself.

The registry records the current directive, scope, hygiene disposition, and source paths. It is a scoped Run Hygiene index; it does not replace other scientific, operational, or authority registries.
