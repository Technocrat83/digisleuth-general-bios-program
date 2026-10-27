# Graph-governed publication: contract candidate v0.1.0

Specimen: `EBA_TEST_001`. Standing: candidate pending review. Production enforcement: NOT_EVALUATED. Release: HOLD.

This is a prospective contract extracted from the unchanged original proposal, not a recovered runtime. F01–F12 retain their original meanings; 34 separately enumerated cases make the previously required subcases explicit. The initial registry records NOT_RUN permanently as the preregistration baseline. Results are separate receipts and never rewrite it.

## Binding and execution sequence

1. Validate and commit this contract. The manifest lists every contract file except itself. It contains no resulting commit hash.
2. Generate a separate receipt that binds the exact manifest and Git blob identities to that prior commit. A later commit can contain that receipt without circularity.
3. Implement the mock against this contract; record any implementation limits. Bind an implementation manifest and its separate commit before execution.
4. Emit one receipt per case. A summary must account for every registered case, including UNRESOLVED and NOT_RUN. Contradictions must not be averaged away.
5. Test real boundary mechanisms separately. Model success cannot promote production enforcement.

## Interpretation of success

SUPPORTED_WITHIN_FIXTURE means all named assertions, authoritative modeled ordering, and independent resource observations for the recorded case agree. CONTRADICTED means a specified expectation failed. UNRESOLVED means necessary observations/order/binding are missing, budgets exceeded, or the apparatus failed. NOT_RUN means no execution occurred. Mock findings are observations against this candidate contract; scientific adjudication and certification remain external.

The checker must inspect resource rows and governing bytes, not infer effects from a rejection log. A checker in the same trusted test process supplies logical separation only; it does not establish operating-system isolation or independence from the test-controller trust domain.

Kernel non-bypassability, tamper resistance, isolation, and atomic authorization-to-commit remain REQUIREMENT_UNESTABLISHED. A single serialized SQLite model can exercise ordering but cannot establish arbitrary external-system atomicity. Signed receipts can support integrity and attribution under their trust assumptions; they cannot establish complete mediation.

## Model envelope and limitations

Synthetic EBA only; no model APIs, payments, messages, or hosting calls. Bounds: 60 seconds, 30 action attempts, three restarts and two retries per intent per case. Modification/deletion are always denied. Drift thresholds are synthetic plumbing values, not calibrated safety limits. The finite graph contract uses typed authority/artifact/review/dependency relations. It is not a general graph rewrite engine, a proof of maximal permissiveness, or evidence of factual research accuracy.

The approved policy and observed execution projection are distinct from worker proposals. High fit never compensates for a failed mandatory predicate. An approval binds exact payload bytes. A checkpoint restores context, never authority. R before D rejects admission; D before R before C_attempt rejects commitment; a prior committed effect remains recorded after a later lock or revocation.

Prior document/schema validation claims remain reported findings. New checks must state the exact bytes and revision they inspected. This package grants no production, canonical promotion, or certification authority.
