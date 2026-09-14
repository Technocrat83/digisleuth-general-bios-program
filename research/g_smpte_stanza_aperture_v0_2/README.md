# G SMPTE STANZA Aperture v0.2

Bounded reference validators for the corrected G_SMPTE_STANZA_APERTURE_v0.2 specification.

## Constitutional boundary

- Code identifies.
- Clock domains anchor temporal coordinates.
- Governance admits states, graph edges, and transitions.
- The aperture projects an already-admitted subgraph.
- Traversal executes only an independently admitted transition.

The validators have no admission, repair, graph-mutation, lifecycle-mutation, sonic-state, or execution authority.

## Components

- src/validators.py: six-coordinate, DAG, and temporal validators.
- fixtures/fixture_cores_v0.2.json: evaluator-visible synthetic inputs with no expected answers.
- oracle/expected_vectors_v0.2.json: evaluator-hidden expected vectors.
- run_blind_battery.py: seeded order, fresh process per fixture, downstream adjudication.
- EXECUTION_RECORD_v0.2.json: bounded synthetic result.

## Reproduce

    python run_blind_battery.py

The result establishes only reference-validator conformance to the frozen synthetic contract.

It does not establish scientific validity, physiological standing, constitutional standing, graph admission, traversal admission, or PP.
